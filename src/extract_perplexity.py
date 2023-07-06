from pathlib import Path

import penman
import torch

from spring.spring_amr import ROOT
from spring.spring_amr.evaluation import extract_amr_perplexity, compute_smatch
from spring.spring_amr.penman import encode
from spring.spring_amr.utils import instantiate_loader, instantiate_model_and_tokenizer

from tqdm import tqdm
import math


def extract_amr_perplexity(loader, model, tokenizer):
    
    beam_size=1
    shuffle_orig = loader.shuffle
    sort_orig = loader.sort

    loader.shuffle = False
    loader.sort = True

    total = len(loader.dataset)
    model.eval()
    model.amr_mode = True

    padding_token_id = 1

    graphs = []

    with tqdm(total=total) as bar:
        for x, y, extra in loader:
            decoder_input_ids = y["decoder_input_ids"]
            labels = y["lm_labels"]
            pred_graphs = extra['graphs']

            # create decoder attention mask
            batch_size = decoder_input_ids.size(0)
            sequence_length = decoder_input_ids.size(1)
            decoder_attention_mask = torch.ones(batch_size, sequence_length, device=decoder_input_ids.device)
            padding_mask = (decoder_input_ids == 1)
            decoder_attention_mask.masked_fill_(padding_mask, 0)

            # calculate logits
            with torch.no_grad():
                loss, logits, *_ = model(input_ids=x["input_ids"],
                                                attention_mask=x["attention_mask"],
                                                decoder_input_ids=decoder_input_ids,
                                                decoder_attention_mask=decoder_attention_mask,
                                                lm_labels=labels)
            
            # calculate perplexity
            for label, logit, graph in zip(labels, logits, pred_graphs):
                score = F.cross_entropy(logit[:len(logit)], label[:len(logit)], ignore_index=padding_token_id)
                graph.metadata["perplexity"] = str(math.exp(loss))
                graphs.append(graph)
    
    return graphs



if __name__ == '__main__':

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(
        description="Script to predict AMR graphs given sentences. LDC format as input.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--pred-path', type=str, required=True, nargs='+',
        help="Required. One or more glob patterns to use to load amr files.")
    parser.add_argument('--perplexity-path', type=Path, default=ROOT / 'data/tmp/perplexity.txt',
        help="Where to write the perplexity file.")
    parser.add_argument('--checkpoint', type=str, required=True,
        help="Required. Checkpoint to restore.")
    parser.add_argument('--model', type=str, default='facebook/bart-large',
        help="Model config to use to load the model class.")
    parser.add_argument('--batch-size', type=int, default=1000,
        help="Batch size (as number of linearized graph tokens per batch).")
    parser.add_argument('--device', type=str, default='cuda',
        help="Device. 'cpu', 'cuda', 'cuda:<n>'.")
    parser.add_argument('--use-recategorization', action='store_true',
        help="Predict using Zhang recategorization on top of our linearization (requires recategorized sentences in input).")
    parser.add_argument('--penman-linearization', action='store_true',
        help="Predict using PENMAN linearization instead of ours.")
    parser.add_argument('--use-pointer-tokens', action='store_true')
    parser.add_argument('--raw-graph', action='store_true')
    parser.add_argument('--restore-name-ops', action='store_true')
    parser.add_argument('--return-all', action='store_true')

    args = parser.parse_args()

    device = torch.device(args.device)
    model, tokenizer = instantiate_model_and_tokenizer(
        args.model,
        dropout=0.,
        attention_dropout=0.,
        penman_linearization=args.penman_linearization,
        use_pointer_tokens=args.use_pointer_tokens,
        raw_graph=args.raw_graph,
    )
    model.amr_mode = True
    model.load_state_dict(torch.load(args.checkpoint, map_location='cpu')['model'])
    model.to(device)

    pred_path = args.pred_path
    perplexity_path = args.perplexity_path
    loader = instantiate_loader(
        args.pred_path,
        tokenizer,
        batch_size=args.batch_size,
        evaluation=True, out=args.perplexity_path,
        use_recategorization=args.use_recategorization,
    )
    loader.device = device

    graphs = extract_amr_perplexity(
        loader,
        model,
        tokenizer
    )
    if args.return_all:
        graphs = [g for gg in graphs for g in gg]

    pieces = [encode(g) for g in graphs]
    
    perplexity_path.write_text('\n\n'.join(pieces))
