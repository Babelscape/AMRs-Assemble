from __future__ import annotations
from collections import defaultdict
from typing import List, Tuple, Optional, Match
import re

class Node:
    def __init__(self, node_id, word, father_node=None, father_relation=None, original_sentence=""):
        self.id = node_id
        self.word = word
        self.child_nodes = []
        self.reference_node = self.word == ""
        self.inverse_node = False
        self.father_node = father_node
        self.father_relation = father_relation

    def get_child_nodes(self):
        return self.child_nodes
        
    def get_child_node(self, relation_name):
        child = None
        for [relation, child_node] in self.get_child_nodes():
            if relation == relation_name:
                child = child_node
        return child
    
    def set_reference_node(self):
        self.reference_node = True
    
    def set_child_node(self, relation_name, child_node):
        self.child_nodes.append([relation_name, child_node])

    def set_inverse_node(self, father_relation):
        self.inverse_node = True
        self.father_relation = father_relation


    def is_correct(self):

        if self.id and self.word and "-" in self.word and self.word.split("-")[-1].isnumeric():
            arguments = []

            if self.father_relation and self.father_relation.endswith("-of"):
                arguments.append(self.father_relation)

            for [relation, _] in self.get_child_nodes():
                if not relation.endswith("-of"):
                    if relation.startswith(":ARG"):
                        arguments.append(relation)

                    elif relation.startswith(":op") or relation.startswith(":snt"):
                        return False
            

            if len(arguments) != len(list(set(arguments))):
                return False
        
        elif self.word and self.word in ["multi-sentence"]:
            arguments = []

            if self.father_relation and self.father_relation.endswith("-of") and self.father_relation.startswith(":ARG"):
                return False

            for [relation, _] in self.get_child_nodes():
                if not relation.endswith("-of"):
                    if relation.startswith(":ARG"):
                        return False

                    elif relation.startswith(":snt"):
                        arguments.append(relation)

                    elif relation.startswith(":op"):
                        return False

            if len(arguments) != len(list(set(arguments))):
                return False

        elif self.word and self.word in ["and", "or", "after", "before"]:
            arguments = []

            if self.father_relation and self.father_relation.endswith("-of") and self.father_relation.startswith(":ARG"):
                return False

            for [relation, _] in self.get_child_nodes():
                if not relation.endswith("-of"):
                    if relation.startswith(":ARG"):
                        return False

                    elif relation.startswith(":op"):
                        arguments.append(relation)

                    elif relation.startswith(":snt"):
                        return False

            if len(arguments) != len(list(set(arguments))):
                return False             

        elif self.word and self.word in ["name"] and self.father_relation and self.father_relation.endswith(":name"):
            arguments = []

            if self.father_relation and self.father_relation.endswith("-of") and self.father_relation.startswith(":ARG"):
                return False

            for [relation, _] in self.get_child_nodes():
                if not relation.endswith("-of"):
                    if relation.startswith(":ARG"):
                        return False

                    elif relation.startswith(":op"):
                        arguments.append(relation)

                    elif relation.startswith(":snt"):
                        return False

            if len(arguments) != len(list(set(arguments))):
                return False  

        elif self.word and self.id and self.word == "date-entity":
            arguments = []
            if self.father_relation and self.father_relation.endswith("-of") and self.father_relation.startswith(":ARG"):
                return False

            for [relation, _] in self.get_child_nodes():
                if not relation.endswith("-of"):
                    if relation.startswith(":ARG"):
                        return False

                    elif relation.startswith(":op") or relation.startswith(":snt"):
                        return False

                    else:
                        arguments.append(relation)

            if len(arguments) != len(list(set(arguments))):
                return False  

        elif self.word and self.id:
            if self.father_relation and self.father_relation.endswith("-of") and self.father_relation.startswith(":ARG"):
                return False

            for [relation, _] in self.get_child_nodes():
                if not relation.endswith("-of"):
                    if relation.startswith(":ARG"):
                        return False

                    elif relation.startswith(":snt"):
                        return False

        # elif connected same children by to edges

        child_ids = []
        relation_ids = []

        if  bool(self.get_child_node(":name")) ^ bool(self.get_child_node(":wiki")):
            return False

        for [relation, child_node] in self.get_child_nodes():
            if child_node.id:
                child_ids.append(child_node.id)

            if  not relation.endswith("of") and (relation.startswith(":ARG") or relation.startswith(":op") or relation.startswith(":snt") or relation in [":name", ":wiki"]):
                relation_ids.append(relation)
        
        if len(child_ids) != len(list(set(child_ids))):
            return False

        if len(relation_ids) != len(list(set(relation_ids))):
            return False



        for [_, child_node] in self.get_child_nodes():
            if not child_node.is_correct():
                return False

        return True
            