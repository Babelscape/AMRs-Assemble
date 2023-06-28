
from regex import R


if __name__ == "__main__":
    sorted_graphs = []
    with open("/home/martinez/project/utils/structural-problems/graphene/graphene_smatch.incorrect.txt", "r") as f:
        for line in f:
            if line.startswith("# ::id "):
                sorted_graphs.append(line.split(" ")[2].strip())

    graphs = {}
    with open("/home/martinez/project/utils/structural-problems/amrbart/pred.test.amrbart.blink.txt", "r") as f:
        new_line = ""
        i = 0
        first = False
        graph = ""
        for line in f:
            if graph and line.startswith("# ::id"):
                graphs[id] = graph

                graph = ""
                id = line.split(" ")[2].strip()

            elif line.startswith("# ::id"):
                id = line.split(" ")[2].strip()

            graph += line

        if graph:
            graphs[id] = graph

    new_line = ""
    for id in sorted_graphs:
        new_line += graphs[id]

    with open("/home/martinez/project/utils/structural-problems/amrbart/pred.test.amrbart.blink.graphene-incorrect.txt", "w") as f:
        f.write(new_line)

                