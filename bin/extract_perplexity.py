from pathlib import Path

import penman
import torch

from spring_amr import ROOT
from spring_amr.evaluation import extract_amr_perplexity, compute_smatch
from spring_amr.penman import encode
from spring_amr.utils import instantiate_loader, instantiate_model_and_tokenizer

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
