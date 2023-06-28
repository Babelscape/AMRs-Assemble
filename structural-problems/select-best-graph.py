import argparse

def select_best_graph(paths, output_path, score_name):
    sorted_graphs = {}
    sorted_scores = {}
    id_sort = []

    for path in paths:
        with open(path, "r") as f:
            print(path)
            graph = ""
            id = ""
            score = None

            for line in f:
                if graph and line.startswith("# ::id"):
                    if id in sorted_graphs:
                        if sorted_graphs[id][1] > score:
                            sorted_graphs[id] = (graph, score)
                    elif id not in sorted_graphs:
                        sorted_graphs[id] = (graph, score)

                    graph = ""
                    id = line.split(" ")[2].strip()
                    graph += line
                    
                elif line.startswith("# ::id"):
                    id = line.split(" ")[2].strip()
                    graph += line

                elif line.startswith(f"# ::{score_name}"):
                    score = float(line.strip().split(" ")[-1].strip())
                    graph += line
                    graph += "# ::model " + path.split("/")[-1] + "\n"

                elif not line.startswith("#"):
                    graph += line

            if graph:
                if id and id in sorted_graphs and sorted_graphs[id][1] > score:
                    sorted_graphs[id] = (graph, score)
                elif id not in sorted_graphs:
                    sorted_graphs[id] = (graph, score)

    new_line = ""
    for g_id, (g, g_score) in sorted_graphs.items():
        new_line += g

    with open(output_path, "w") as f1:
        f1.write(new_line)

    print(f"Best graph selected and saved to {output_path}")


                


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select the graph with the highest score from multiple files.")
    parser.add_argument("--paths", nargs="+", help="Paths to the input files")
    parser.add_argument("--output", default="data/tmp/max_perplexity.txt", help="Output file path")
    parser.add_argument("--score-name", default="perplexity",  help="Type of score to consider (perplexity or scr)")
    args = parser.parse_args()

    select_best_graph(args.paths, args.output, args.score_name)