import re
import matplotlib.pyplot as plt, numpy as np
from pathlib import Path

## script in order to analyze the previously calculated data

directoryPrefix = "BipolarADF_StatementSize_"

# for a specified statement size and semantics retrieve all results and determine average time for the calculation of one model
# time is determined for the two calculation styles of two-valued completion and three-valued logic
def get_results(statement_size, semantics):
    # retrieved eval files should contain the correct statement size
    proxy_expr = r"Eval.*StatementSize_" + str(statement_size) + "_"
    # specify that tri evaluation shall not be loaded

    # check for lookahead
    # negative lookahaed
    twoValCompl = proxy_expr + r".*Sem_(?!.*tri|twoValOpt).*" + ",".join(semantics)
    twoValCompl = re.compile(twoValCompl)
    twoValComplPath

    # use optimized version for calculation of semantics
    # positive lookahead
    twoValComplOpt =  proxy_expr + r".*Sem_(?=.*twoValOpt).*" + ",".join(semantics)
    twoValComplOptPath

    # specify that tri evaluation shall be loaded
    # positive lookahead
    threeLogics = proxy_expr + r".*Sem_(?=.*tri).*" + ",".join(semantics)
    threeLogics = re.compile(threeLogics)
    threeLogicsPath


    class_models = retrieveVal(statement_size, twoValCompl)
    tri_models = retrieveVal(statement_size, threeLogics)

    # divide time by 10 to get time for a single model
    # a = np.array(class_models) # debug variable
    class_models_rd = np.divide(np.array(class_models),10)
    tri_models_rd =np.divide(np.array(tri_models),10)

    meanTwoValCompl = np.mean(class_models_rd)
    mtri = np.mean(tri_models_rd)
    # print information about total number of models found and the average time
    # print("Retrieved Results for StatementSize:{} - Semantics:{}".format(statement_size,semantics))
    # print("TwoValued Nbr.Models:{} - AvgTime:{}".format(len(class_models),meanTwoValCompl))
    # print("TriValued Nbr.Models:{} - AvgTime:{}".format(len(tri_models),mtri))
    return (statement_size, meanTwoValCompl, mtri)

# retrieve calculation time from evaluated data for specific statement size and store results in a lists, filename is specified by regexpr
def retrieveVal(statement_size, regexpr):
    path_for_search = Path.joinpath(Path.cwd(), directoryPrefix + str(statement_size))
    time_results = []
    for filePathName in path_for_search.iterdir():
        if regexpr.search(filePathName.name):
            with open(filePathName,"r") as calc_results:
                for line in calc_results:
                    if line.startswith("#"): # filter out comments
                        continue
                    if line.startswith("Model"):
                        continue
                    if line.startswith("Semantics:"):
                        evaluated = eval(line.replace("Semantics:", ""))
                        time_results.append(evaluated[0])
            calc_results.close()
    return time_results


# check length of models for a distinct statement size and semantics, the latter is handled as regexpr
def modelCounter(statement_size, regexpr):
    path_for_search = Path.joinpath(Path.cwd(), directoryPrefix + str(statement_size))
    models = []
    for filePathName in path_for_search.iterdir():
        if regexpr.search(filePathName.name):
            with open(filePathName,"r") as calc_results:
                for line in calc_results:
                    if line.startswith("#"): # filter out comments
                        continue
                    if line.startswith("Model"):
                        evaluated = line.replace("Model:", "")
                        models.append(evaluated)
                        continue
                    if line.startswith("Semantics:"):
                        continue
            calc_results.close()
    return (len(models)),(len(set(models)))

# search for models in the calculated evaluation files and return number of models; is used to check that all generated models have been calculated
# number of models should equal the number of models, which were created before
# in addition we check how many models are unique, for statement size greater than 3 all models should be unique
def countModels(min,max,semantics):
    print("Counting models in eval files and determining how many are unique")
    for statementSize in range(min,max+1):
        proxy_expr = r"Eval.*StatementSize_" + str(statementSize) + "_"
        # do not load tri evaluation
        two_expr = proxy_expr + r".*Sem_(?!.*tri).*" +  ",".join(semantics)
        two_expr = re.compile(two_expr)
        twoRes = modelCounter(statementSize,two_expr)

        # load tri evaluation
        tri_expr = proxy_expr + r".*Sem_(?=.*tri).*"  +  ",".join(semantics)
        tri_expr = re.compile(tri_expr)
        triRes = modelCounter(statementSize, tri_expr)

        print("StatementSize:{} Semantics:{}".format(statementSize,semantics))
        # print how many models have been found and how many models are unique
        print("TwoValued NbrModels:{} - NbrUnique:{}".format(twoRes[0],twoRes[1]))
        print("TriValued NbrModels:{} - NbrUnique:{}".format(triRes[0],triRes[1]))
    print("\n")

# check models from statement size 1 to 8 for admissible interpretation
countModels(1,8,["a"])

# for specified statement size range and semantics plot the average time for the two and three-valued style
# min and max are specifying the range for the displayed statement size; sem1,sem2 are specifying the semantics
# sem1note; sem2note are specifying the description of the used semantics in the legend
def plot_gain(min,max,sem1,sem2,sem1note,sem2note):
    # collect two and three-valued results for sem1
    sem1_final = []
    for statementSize in range(min,max+1):
        result = get_results(statementSize, sem1)
        sem1_final.append(result)
    sem_statements_1 = list(map( lambda  x: x[0],sem1_final))
    class_time_1 = list(map( lambda  x: x[1],sem1_final))
    tri_time_1 = list(map( lambda  x: x[2],sem1_final))

    # collect two and three-valued results for sem2
    sem2_final = []
    for statementSize in range(min, max + 1):
        result = get_results(statementSize, sem2)
        sem2_final.append(result)
    sem_statements_2 = list(map(lambda x: x[0], sem2_final))
    class_time_2 = list(map(lambda x: x[1], sem2_final))
    tri_time_2 = list(map(lambda x: x[2], sem2_final))

    # create a plot
    font = {'family': 'normal',
            'weight': 'normal',
            'size': 50}

    plt.rc('font', **font)
    fig, ax = plt.subplots()

    ax.plot(sem_statements_1,class_time_1,label=sem1note+"-two",linewidth=3,color ="b", linestyle="-")
    ax.plot(sem_statements_1,tri_time_1,label= sem1note + "-tri",linewidth=3,color ="b",linestyle="dotted")
    ax.plot(sem_statements_2,class_time_2,label= sem2note +"-two",linewidth=3,color ="r", linestyle="-")
    ax.plot(sem_statements_2,tri_time_2,label=sem2note+"-tri",linewidth=3,color ="r",linestyle="dotted")

    ax.set_ylabel('Time in Seconds',fontsize="medium")
    ax.set_xlabel('Number of Statements',fontsize="medium")
    ax.set_aspect('equal', adjustable='box')
    plt.yscale("log")
    plt.legend(loc='best')
    ax.legend(loc='upper left')
    fig.tight_layout()
    # ax.yaxis(fontsize="medium")
    ax.set_xlim(xmin=1, xmax=len(sem_statements_1))
    plt.xticks([x for x in range(1,9)])
    # ax.set_title('Comparison of Admissible and Complete Semantics',fontsize="medium")
    plt.show()


# helper in order to collect data which is needed to create a table; collected semantics are specified in the corresponding variable
# for each specified semantics we collect the average time of the two-valued completion and the three-valued logic approach
# in addition we calculate the speed factor, indicating how much faster the latter approach is
# range below specifies which statement size shall be included in the collected data
def tablecontent_creator():
    # semantics = [["a"],["c"],["p"]
    semantics = [["a"],["c"]]

    # create head
    table_head = ["Size"]
    for singSem in semantics:
        table_head += ["{}".format(singSem), "tri-{}".format(singSem), "Speed"]
    final_table = [table_head]

    # create body
    for statement_size in range(1,9):
        table_row = [statement_size]
        for singSem in semantics:
            nbr,two,tri = get_results(statement_size,singSem)
            speed = np.divide(two,tri)
            [table_row.append(x) for x in [two,tri,speed]]
        final_table.append(table_row)
    return final_table
tablecontent_creator()

# tex style writer for data obtained by tablecontent_creator
def mult_tex_writer(dataTable):
    lendatastream = len(dataTable[0])
    templaterowTemp = r"{}\\"
    dataheadraw = "{}&" * lendatastream
    dataheadraw = dataheadraw[:-1] # remove ampersand
    datahead = dataheadraw.format(*dataTable[0])
    print("\\begin{tabular}{" + ("c|" * len(dataTable[0]))[:-1] + "}")
    print(templaterowTemp.format(datahead))
    for dataRow in dataTable[1:]:
        dataRowRaw = "${}$&" * lendatastream
        dataRowRaw = dataRowRaw[:-1]
        rounded = [np.round(x, 4) for x in dataRow[:-1]]
        rounded.append(np.round(dataRow[-1], 2))
        formated = dataRowRaw.format(*rounded)
        print(templaterowTemp.format(formated))
    print("\\end{tabular}")

# html style writer for data obtained by tablecontent_creator
def mult_html_writer(dataTable):
    lendatastream = len(dataTable[0])
    templaterowTemp = r"<tr>{}$</tr>"
    dataheadraw = "<th>{}</th>" * lendatastream
    datahead = dataheadraw.format(*dataTable[0])
    print("<table>")
    print(templaterowTemp.format(datahead))
    for dataRow in dataTable[1:]:
        dataRowRaw = "<td>{}</td>" * lendatastream
        rounded = [np.round(x, 4) for x in dataRow[:-1]]
        rounded.append(np.round(dataRow[-1], 2))
        formated = dataRowRaw.format(*rounded)
        print(templaterowTemp.format(formated))
    print("</table>")


# mult_html_writer(tablecontent_creator())
mult_tex_writer(tablecontent_creator())
plot_gain(1,8,["a"],["c"],"adm","cmp")


