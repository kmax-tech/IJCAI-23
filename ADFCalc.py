# This script calculates the semantics of ADFs,therefore the variables nodes and chooseinterpretations have to be edited by the user
import itertools, re, functools, time

# enter each node (n) and its acceptance condition (ac) as a list [n,ac] into the variable nodes
# syntax: (,) for logical and, (;) for logical or, (#) for negation, also parentheses are allowed

# nodes = [["b","#w,b"],["h","(w;b)"],["r","?"],["s","h,b"],["w","#r,#b"]]
# chooseinterpretations= ["a","c","p","tri"]

nodes = [["j","s;(m,#w)"],["s","s"],["m","!"],["w","?"]]
semantics= ["a", "c", "p"]

# optimizer, here one can twoOpt and tri in order to speed up the calculation
# twoOpt first looks for nodes, where no two-valued completion is required, tri is using a three-valued logic
optimizer = "tri"
# Possible Semantics
# admissible (a), complete (c), preferred(p), ground(g)


# parse ADF into calculation format
class ParseAndPrepare():
    def __init__(self, inp, desiredSemantics):
        self.desiredSemantics = desiredSemantics
        self.formulas = inp
        self.nodeNames = self.get_nodenames(self.formulas)
        self.nbrNodes = len(self.nodeNames)  #number of nodes used
        self.triValues = ["0.0", "0.5", "1.0"] #for calculation with Kleene's strong three-valued logic
        self.twoValues = ["False", "u", "True"] #for calculation with Python build-in boolean logic
        self.twoValuedConnectives = [(",", " and "), (";", " or "), ("#", " not "), ("!", " True "), ("?", " False ")]
        self.triValuedConnectives = [(",", " & "), (";", " | "), ("#", " ~ "), ("!", " ThreeLogics(1) "), ("?", " ThreeLogics(0) ")]


        if optimizer == "tri":
            self.interpretations = self.create_all_interpretations(self.triValues)
            self.preparedFormulas = self.parse_acceptance_condition(self.parse_formula(), self.triValuedConnectives)
            self.undefinedNode = "0.5"
        else:
            self.interpretations = self.create_all_interpretations(self.twoValues)
            self.preparedFormulas = self.parse_acceptance_condition(self.parse_formula(), self.twoValuedConnectives)
            self.undefinedNode = "u"

    # get the used nodeNames and sort out possible duplicates
    def get_nodenames(self, inp):
        nodeNames = set()
        [nodeNames.add(x[0]) for x in inp]
        if len(nodeNames) != len(inp):
            print("Number of distinct nodenames is not number of nodes/acceptance conditions!")
            raise ValueError
        return list(sorted(nodeNames))

    # create all possible interpretations
    # use of generator because of possible list size
    def create_all_interpretations(self, x):
        for interpretation in itertools.product(x, repeat=self.nbrNodes):
            testit = dict(zip(self.nodeNames, interpretation))
            yield testit

    # parse acceptance condition; logical connectives are replaced with their corresponding semantical connectives
    def parse_acceptance_condition(self, inp, connectives):
        for x in inp:
            for ind,lit in enumerate(x[1]):
                x[1][ind] = (functools.reduce(lambda x, y: x.replace(y[0], y[1]), ([lit] + connectives)))
        return inp

    # find positions of other nodes in an acceptance condition
    # acceptance condition string is converted to a list
    def convert_acceptance_condition_to_list_representation(self, input):
        regex = "|".join(sorted(self.nodeNames, key=len, reverse=True))
        # determine span of used nodes in an acceptance condition
        nodesPositions = tuple(x.span() for x in re.finditer(regex, input))
        notNodePositions = list(map(lambda x, y: (x[1], y[0]), ((0, 0),) + nodesPositions, nodesPositions + ((None, None),)))
        # chain position together and split acceptance condition into a corresponding string
        return [input[x:y] for x, y in sorted(itertools.chain(list(nodesPositions), notNodePositions))]

    # for an efficient replacement of the interpretation value the positions of all nodes in an acceptance condition are marked
    def find_list_index(self, input):
        startindex = {node: [] for node in self.nodeNames if node in input}  #an empty dictionary for the formula
        [startindex[node].append(position) for position, node in enumerate(input) if node in startindex]  #add the positions of the formulas
        return startindex

    # parse node and aceeptance condition, evaluable format
    def parse_node_acceptance_condition(self, node, formula):
        subs = self.convert_acceptance_condition_to_list_representation(formula)
        return ([node, subs, self.find_list_index(subs)])

    def parse_formula(self): #sort according to the amount of nodes in an acceptance condition
        return sorted([self.parse_node_acceptance_condition(node, formula) for node, formula in self.formulas], key=lambda form: len(form[2]))

class ThreeLogics: #an implementation of Kleenes strong three-valued logic
    def __init__(self, a):
        self.a = float(a)
    def __str__(self):
            return str(self.a)
    def __and__(self, o):
        return ThreeLogics(min(self.a,o.a))
    def __or__(self, o):
        return ThreeLogics(max(self.a,o.a))
    def __invert__(self):
        return ThreeLogics(1 - self.a)

class EvaluateAndInterprete(ParseAndPrepare): #this class inherits the prepared formulas from parseandprepare and evaluates the interpretations
    def __init__(self, formulas, desiredSemantics):
        ParseAndPrepare.__init__(self, formulas, desiredSemantics)
        # pre and post strings for better formatting
        if self.undefinedNode == "u":
            self.pre = ""
            self.post = ""
        else:
            self.pre = " ThreeLogics("
            self.post = ") "

    # evaluates all nodes, given an interpretation
    def formulaeEvaluation(self,parsedFormulae,interpretation):
        calculatedInterpretation = {}  #we start with an empty dictionary for the final interpretations
        for formula in parsedFormulae:
            for node, index in formula[2].items():
                for position in index:
                        formula[1][position] = self.pre + interpretation[node] + self.post
            calculatedInterpretation.update({formula[0]: str(eval("".join(formula[1])))})
        return calculatedInterpretation


    # evaluates according to the gamma operator with the Python built in two-valued logic
    def gammaOp_TwoVal(self, interpretation):
        undefinedNodes = []  #to mark the nodes which values are undefined in an interpretation
        usedNodesEvaluation = [node for node in self.nodeNames]
        twoValuedInterpretation = {}
        finalGammaInterpretation = {}
        for node, value in interpretation.items(): #filter out nodes, which don't have the value undefined
            if value != "u":  #for other values than u, the completion has the exact same values
                twoValuedInterpretation.update({node: value})
            else:
                undefinedNodes.append(node)
        if undefinedNodes == []:  #means that we have no undefined values in the interpretation and need no two-valued completions
            return self.formulaeEvaluation(self.preparedFormulas, twoValuedInterpretation)
        interpretationGenerator = itertools.product(["True", "False"], repeat=len(undefinedNodes)) #for the undefined nodes the two-valued completions are generated
        # take the first value from the generator and create interpretation for the comparison
        firstValue = next(interpretationGenerator)
        gammaBaseInterpretationEvaluated = self.formulaeEvaluation(self.preparedFormulas, {**twoValuedInterpretation, **dict(zip(undefinedNodes, firstValue))})
        for truthValueTuples in interpretationGenerator:

            currentInterpretationUndefinedNodes = dict(zip(undefinedNodes, truthValueTuples))
            # add the two-valued interpretation from nodes which are not undefined, and eval the values
            currentTwoValuedCompletitionEvaluated = self.formulaeEvaluation(self.preparedFormulas, {**twoValuedInterpretation, **currentInterpretationUndefinedNodes})  #the current calculated two-valued interpretation

            if usedNodesEvaluation!= []:
                differentValues = set(gammaBaseInterpretationEvaluated.items()) - set(currentTwoValuedCompletitionEvaluated.items())  #find interpretations, which are different in the two sets
                for node, value in differentValues:
                    if node in usedNodesEvaluation:
                        finalGammaInterpretation.update({node: "u"})  #for the nodes in differentValues the value of the gammaoperators is "u"
                        # remove the nodes to mark that the gamma interpretation of them has been found
                        usedNodesEvaluation.remove(node)
            else:  # means that we found every evaluation for the gamma operator
                break

        # for all possible completions the code stayed the same, in this case the interpretation are taken from the first evaluated intperpretation, to obtain the values in the gamma interpretation
        for node in usedNodesEvaluation:
            finalGammaInterpretation.update({node: gammaBaseInterpretationEvaluated[node]})

        return finalGammaInterpretation


    # slightly optimized Version for solving, first the formulae are calculated for which no two-valued completion is needed
    def gammaOp_TwoValOptimized(self, interpretation):
        undefinedNodes = []  #to mark the nodes which values are undefined in an interpretation
        usedNodesEvaluation = [node for node in self.nodeNames]
        twoValuedInterpretation = {}
        finalGammaInterpretation = {}
        for node, value in interpretation.items(): #filter out nodes, which don't have the value undefined
            if value != "u":  #for other values than u, the completion has the exact same values
                twoValuedInterpretation.update({node: value})
            else:
                undefinedNodes.append(node)
        if undefinedNodes == []:  #means that we have no undefined values in the interpretation and need no two-valued completions
            return self.formulaeEvaluation(self.preparedFormulas, twoValuedInterpretation)

        # check if the two valued interpretations are sufficient alone to implement
        twoValuedNodesSet = set(twoValuedInterpretation.keys())
        twoValuedEvaluableFormulas = [] # split the list of parsed formulas into ones, where conventional logic can be used
        twoValuedCompletionFormulas = [] #for these formulas the two-valued completion approach is required

        for model in self.preparedFormulas:
            modelset = set(model[2])
            if modelset.issubset(twoValuedNodesSet):
                twoValuedEvaluableFormulas.append(model)
            else:
                twoValuedCompletionFormulas.append(model)

        # calculate the nodes, where no two-valued completion is required
        twoValuedEvaluableFormulasEvaluated = self.formulaeEvaluation(twoValuedEvaluableFormulas,twoValuedInterpretation)
        print("EvalSafe",twoValuedEvaluableFormulasEvaluated)
        for node,value in twoValuedEvaluableFormulasEvaluated.items():
            usedNodesEvaluation.remove(node)
            finalGammaInterpretation.update({node:value})

        # now calculate two-valued completions
        interpretationGenerator = itertools.product(["True", "False"], repeat=len(undefinedNodes)) #for the undefined nodes the two-valued completions are generated
        # take the first value from the generator and create interpretation for the comparison
        firstValue = next(interpretationGenerator)
        gammaBaseInterpretationEvaluated = self.formulaeEvaluation(twoValuedCompletionFormulas,{**twoValuedInterpretation, **dict(zip(undefinedNodes, firstValue))})
        for truthValueTuples in interpretationGenerator:

            currentInterpretationUndefinedNodes = dict(zip(undefinedNodes, truthValueTuples))

            # add the two-valued interpretation from nodes which are not undefined, and eval the values
            currentTwoValuedCompletitionEvaluated = self.formulaeEvaluation(twoValuedCompletionFormulas,{**twoValuedInterpretation, **currentInterpretationUndefinedNodes})  #the current calculated two-valued interpretation

            if usedNodesEvaluation!= []:
                differentValues = set(gammaBaseInterpretationEvaluated.items()) - set(currentTwoValuedCompletitionEvaluated.items())  #find interpretations, which are different in the two sets
                for node, value in differentValues:
                    if node in usedNodesEvaluation:
                        finalGammaInterpretation.update({node: "u"})  #for the nodes in differentValues the value of the gammaoperators is "u"
                        # remove the nodes to mark that the gamma interpretation of them has been found
                        usedNodesEvaluation.remove(node)
            else:  # means that we found every evaluation for the gamma operator
                break

        # for all possible completions the code stayed the same, in this case the interpretation are taken from the first evaluated intperpretation, to obtain the values in the gamma interpretation
        for node in usedNodesEvaluation:
            finalGammaInterpretation.update({node: gammaBaseInterpretationEvaluated[node]})

        return finalGammaInterpretation



    # calculation based on three-valued logic
    def gammaOp_threeValLogics(self, interpretation):
        return self.formulaeEvaluation(self.preparedFormulas, interpretation)

    def ground_calc(self, x):
        interpretation = dict(zip(self.nodeNames, [self.undefinedNode] * self.nbrNodes)) #we start with the interpretation, where everything is set to undefined
        #print("interpretation", interpretation)
        gammainterpretation = x(interpretation)
        #print("gammaint", gammainterpretation)
        while (interpretation != gammainterpretation):
            interpretation = gammainterpretation
            gammainterpretation = x(gammainterpretation)
            #print("gammaint", gammainterpretation)
        return gammainterpretation

    # list the calculated interpretations
    def enumerated_printing(self, inlist):
        for index, x in enumerate(inlist):
            print("Nr.{}".format(index + 1) , [node + ":" + value for node,value in sorted(x.items())], "\n")

    def gamma_compare(self, interp, gammaInterpretation):  #compares two evaluations
        for node in self.nodeNames:
            if (interp[node] != self.undefinedNode) and (interp[node] != gammaInterpretation[node]):
                return 0
        return gammaInterpretation

class ControlAndPrint(EvaluateAndInterprete):
    def __init__(self, formulas, desiredSemantics):
        EvaluateAndInterprete.__init__(self, formulas, desiredSemantics)

        # determine which calculation style should be used
        if optimizer == "tri":
            self.gamma = self.gammaOp_threeValLogics
        elif optimizer == "twoValOpt":
            self.gamma = self.gammaOp_TwoValOptimized
        # standard method for calculation
        else:
            self.gamma = self.gammaOp_TwoVal

    # compare two interpretations wrt. their information content
    def interpretationMoreContent(self, interpretation1, interpretation2):
        marker = []
        for node in interpretation1:
            if (interpretation1[node]) != self.undefinedNode and (interpretation1[node] == interpretation2[node]):
                continue
            if (interpretation1[node]) != self.undefinedNode and (interpretation1[node] != interpretation2[node]):
                return -1  #here interpretation2 is not more admissible than interpretation1
            if (interpretation1[node]) == self.undefinedNode and (interpretation2[node] != self.undefinedNode):
                marker.append("x")
            else:
                continue
        return 1  #interpretation2 is more admissible

    def preferred(self,interpretations):
        leninters = len(interpretations) - 1
        prefinterpretations = []  #we start with an empty list
        for index, testval in enumerate(interpretations):
            checkinterpretation = 0
            for testinterpretation in (interpretations[0:index] + interpretations[index + 1:]):
                calcvalue = self.interpretationMoreContent(testinterpretation, testval)
                if calcvalue == 1:
                    checkinterpretation += 1
                if calcvalue == -1:
                    if self.interpretationMoreContent(testval, testinterpretation) == -1:
                        checkinterpretation += 1
                    else:
                        break  #we found an counterexample which is more admissible, that's why the search can be stopped here
            if (checkinterpretation == leninters):  #testval is more admissible than any other interpretation
                prefinterpretations.append(testval)
                continue
        return prefinterpretations

    def interpretationEvaluator(self):
        interpretationAdm = [] #list of final interpretations, admissible, complete, preferred, ground
        interpretationComp = []
        interpretationPrf = []
        interpretationGRD = []
        if (("a" in self.desiredSemantics) or ("c" in self.desiredSemantics) or ("p" in self.desiredSemantics)):
            for interpretation in self.interpretations:
                gammatemp = self.gamma_compare(interpretation, self.gamma(interpretation))
                if "a" in self.desiredSemantics:
                    if gammatemp != 0:
                        interpretationAdm.append(interpretation)
                if (("p" in self.desiredSemantics) or ("c" in self.desiredSemantics)):
                    if gammatemp == interpretation:
                        interpretationComp.append(interpretation)
            if "p" in self.desiredSemantics:
                interpretationPrf = (self.preferred(interpretationComp))
        if "g" in self.desiredSemantics:
            interpretationGRD.append(self.ground_calc(self.gamma))
        result = [interpretationAdm, interpretationComp, interpretationPrf, interpretationGRD]
        return result

    def interpretationPrinter(self):
        inter = self.interpretationEvaluator()
        if "a" in self.desiredSemantics:
            print("Admissible Interpretations \n")
            self.enumerated_printing(inter[0])
        if "c" in self.desiredSemantics:
            print("Complete Interpretations \n")
            self.enumerated_printing(inter[1])
        if "p" in self.desiredSemantics:
            print("Preferred Interpretations \n")
            self.enumerated_printing(inter[2])
        if "g" in self.desiredSemantics:
            print("Ground Interpretations \n")
            self.enumerated_printing(inter[3])

if __name__ == "__main__":
    x = ControlAndPrint(nodes, semantics)
    print("Formatted Formula \n")
    print(x.preparedFormulas, "\n")
    start = time.time()
    x.interpretationPrinter()
    end = time.time()
    print("Total Time")
    print(end - start)





