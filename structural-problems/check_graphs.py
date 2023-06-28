import graph_parser
import re
import amr
from penman import loads
import argparse

is_amr_id = re.compile(r'^[a-z]([1-9]{0,1})([0-9]{0,1})$')

def parse_sentence(sentence, father_node=None, father_relation=None,  original_sentence=""):
    tokens_sentence = sentence.split(" ")

    node_id = tokens_sentence[0][1:].strip()
    node_word = tokens_sentence[2].strip()

    while node_word.endswith(")"):
        node_word = node_word[:-1]

    parenthesis_number = 0
    tokens_iterator = 3
    node = graph_parser.Node(node_id, node_word, father_node, father_relation, original_sentence)
    

    while len(tokens_sentence) > tokens_iterator and tokens_sentence[tokens_iterator].startswith(":"):
        if tokens_sentence[tokens_iterator].startswith(":ARG") and not tokens_sentence[tokens_iterator + 1].startswith("("):
            lit_pos = 1
            word = tokens_sentence[tokens_iterator + lit_pos].strip()
            while word.endswith(")"):
                word = word[:-1]

            if word.startswith("\""):
                word = word
                while not word.split("~e.")[0].endswith("\""):
                    lit_pos += 1
                    word = word + " " + tokens_sentence[tokens_iterator + lit_pos].strip()


                if "~e." in word:
                    word = word.split("~e.")[0] + "~e." + word.split("~e.")[1]
                else:
                    word = word
                
            if is_amr_id.match(word.split("~e.")[0]):
                child_node = graph_parser.Node(word, "", node, tokens_sentence[tokens_iterator].strip().split("~")[0], original_sentence)
            else:
                child_node = graph_parser.Node("", word, node, tokens_sentence[tokens_iterator].strip().split("~")[0], original_sentence)
            
            node.set_child_node(tokens_sentence[tokens_iterator].strip().split("~")[0], child_node)


            tokens_iterator += lit_pos + 1


        elif not tokens_sentence[tokens_iterator + 1].startswith("("):
            word = tokens_sentence[tokens_iterator + 1].strip()

            if tokens_sentence[tokens_iterator + 1].startswith('"') and tokens_sentence[tokens_iterator + 1].count('"') == 1:
                next_pos = 2
                while '"' not in tokens_sentence[tokens_iterator + next_pos]:
                    word += " " + tokens_sentence[tokens_iterator + next_pos].strip()
                    next_pos += 1
                
                word += " " + tokens_sentence[tokens_iterator + next_pos].strip()


            while word.endswith(")"):
                word = word[:-1]

            if is_amr_id.match(word):
                child_node = graph_parser.Node(word, "", node, tokens_sentence[tokens_iterator].strip().split("~")[0], original_sentence)
            else:
                child_node = graph_parser.Node("", word, node, tokens_sentence[tokens_iterator].strip().split("~")[0], original_sentence)


            node.set_child_node(tokens_sentence[tokens_iterator].strip().split("~")[0], child_node)
            tokens_iterator += 2

        else:
            subsentence = tokens_sentence[tokens_iterator + 1].strip() + " "
            parenthesis_iterator = tokens_iterator + 2
            parenthesis_number += 1
            while parenthesis_number > 0:
                
                token = tokens_sentence[parenthesis_iterator].strip()

                if token.startswith("("):
                    parenthesis_number += 1
                elif token.endswith(")"):
                    while token.endswith(")"):
                        token = token[:-1]
                        parenthesis_number -= 1

                subsentence += tokens_sentence[parenthesis_iterator].strip() + " "
                parenthesis_iterator += 1

            subsentence = subsentence[:-1]
            child_node = parse_sentence(subsentence, node, tokens_sentence[tokens_iterator].strip().split("~")[0], original_sentence)

            if tokens_sentence[tokens_iterator].endswith("-of"):
                child_node.set_inverse_node(tokens_sentence[tokens_iterator].strip())

            node.set_child_node(tokens_sentence[tokens_iterator].strip().split("~")[0], child_node)
            tokens_iterator = parenthesis_iterator

    return node


def write_graphs(output_file, newgraphs_metadata):
    # write graphs to file
    with open(output_file, 'w') as outfile:
        new_sentences = []
        for key, value in newgraphs_metadata.items():
            rootnode = value["graph"]
            graph_id = value["id"]
            sentence = value["sentence"]
            graph_sentence = value["graph_sentence"]

            new_string_graph = graph_id.strip() + "\n" + sentence.strip() + "\n" + graph_sentence + "\n"
            new_sentences.append(new_string_graph)
            
        outfile.write("\n".join(new_sentences))

def read_check_graphs(file_path):
    correct_graph_map = {}
    incorrect_graph_map = {}

    with open(file_path, 'r') as graph_file: 
        graph_id = ""
        id = ""
        graph_sentence = ""
        graph_sentence_strip = ""
        metadata = ""
        snt = ""

        for line in graph_file:
            if line.startswith('# ::snt'):
                if graph_sentence:
                    try: 
                        node = parse_sentence(graph_sentence_strip, father_node=None, original_sentence=snt.split("::snt")[1].strip())
                        corrupted = False
                        if not amr.AMR.parse_AMR_line(graph_sentence):
                            corrupted = True
                        loads(graph_sentence)
                    except:
                        corrupted = True

                    if node.is_correct() and not corrupted:
                        correct_graph_map[id] = {
                            "graph": node,
                            "id": graph_id,
                            "sentence": snt,
                            "metadata": metadata,
                            "graph_sentence": graph_sentence
                        }
                    else:
                        incorrect_graph_map[id] = {
                            "graph": node,
                            "id": graph_id,
                            "sentence": snt,
                            "metadata": metadata,
                            "graph_sentence": graph_sentence
                        }

                    id = ""
                    graph_id = ""
                    snt = ""
                    metadata = ""
                    graph_sentence = ""
                    graph_sentence_strip = ""
                snt = line.strip()

            elif line.startswith('# ::id'):
                id = line.split("::amr-annotator", 1)[0].split(' ')[2].strip()
                graph_id = line.strip()
                
            elif line.startswith('#'):
                metadata += line

            elif line.strip() and not line.startswith('#'):
                graph_sentence_strip += line.strip() + " "
                graph_sentence += line

        if graph_id:
            node = parse_sentence(graph_sentence, father_node=None, original_sentence="")
            corrupted = False
            try: 
                if not amr.AMR.parse_AMR_line(graph_sentence):
                    corrupted = True
                loads(graph_sentence)
            except:
                corrupted = True
            
            if node.is_correct() and not corrupted:
                correct_graph_map[id] = {
                    "graph": node,
                    "id": graph_id,
                    "sentence": snt,
                    "metadata": metadata,
                    "graph_sentence": graph_sentence
                }
            else:
                incorrect_graph_map[id] = {
                    "graph": node,
                    "id": graph_id,
                    "sentence": snt,
                    "metadata": metadata,
                    "graph_sentence": graph_sentence
                }

    return correct_graph_map, incorrect_graph_map
            

def filter_graphs(input_file):
    # Define the file paths
    file = input_file
    correct_output = file.replace(".txt", ".correct.txt")
    incorrect_output = file.replace(".txt", ".incorrect.txt")

    # Read and check graphs for correctness
    correct, incorrect = read_check_graphs(file)

    # Write correct and incorrect graphs to separate files
    write_graphs(correct_output, correct)
    write_graphs(incorrect_output, incorrect)

    # Get IDs of correct graphs
    correct_graph_ids = list(correct.keys())

    # Write correct graph IDs to a separate file
    with open(file.replace(".txt", ".correct-ids.txt"), "w") as f:
        f.write("\n".join(correct_graph_ids))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter graphs based on correctness.')
    parser.add_argument('--input', type=str, help='Input file path')
    args = parser.parse_args()

    # Filter graphs
    filter_graphs(args.input)

