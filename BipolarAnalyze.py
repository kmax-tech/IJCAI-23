import re
import matplotlib.pyplot as plt, numpy as np
from pathlib import Path

# load time and get average of results
def get_results(nodesize,semantics):
    proxy_expr = r"Eval.*Nodes_"+str(nodesize) + "_"
    # specify that tri evaluation shall not be loaded
    class_expr = proxy_expr + r".*Sem_(?!.*tri).*" +  ",".join(semantics)
    class_expr = re.compile(class_expr)
    # specify that tri evaluation shall be loaded
    tri_expr = proxy_expr + r".*Sem_(?=.*tri).*"  +  ",".join(semantics)
    tri_expr = re.compile(tri_expr)
    class_models = retrieveVal(nodesize,class_expr)
    tri_models = retrieveVal(nodesize,tri_expr)

    # do division according to the NodeSize
    #a = np.array(class_models) # debug variable
    class_models_rd = np.divide(np.array(class_models),10)
    tri_models_rd =np.divide(np.array(tri_models),10)

    mclass = np.mean(class_models_rd)
    mtri = np.mean(tri_models_rd)
    # print information about total number of models found and the average time
    #print("Info about Nodesize: {} Semantics:{}".format(nodesize,semantics))
    #print("TwoValued Nbr.Models:{} - AvgTime:{}".format(len(class_models),mclass))
    #print("TriValued Nbr.Models:{} - AvgTime:{}".format(len(tri_models),mtri))
    return (nodesize,mclass,mtri)

# retrieve time from calculated data, filename is specified by the regex
def retrieveVal(nodenbr, regexpr):
    path_for_search = Path.joinpath(Path.cwd(),"BipolarNodes_{}".format(nodenbr))
    class_time = []
    for filePathName in path_for_search.iterdir():
        if regexpr.search(filePathName.name):
            with open(filePathName,"r") as calc_results:
                for line in calc_results:
                    if line.startswith("#"): #filter out comments
                        continue
                    if line.startswith("Model"): #filter out comments
                        continue
                    if line.startswith("Semantics:"):
                        evaluated = eval(line.replace("Semantics:", ""))
                        class_time.append(evaluated[0])
            calc_results.close()
    return class_time


# check length of models for a distinct nodenbr
def modelCounter(nodenbr,regexpr):
    path_for_search = Path.joinpath(Path.cwd(),"BipolarNodes_{}".format(nodenbr))
    models = []
    for filePathName in path_for_search.iterdir():
        if regexpr.search(filePathName.name):
            with open(filePathName,"r") as calc_results:
                for line in calc_results:
                    if line.startswith("#"): #filter out comments
                        continue
                    if line.startswith("Model"): #filter out comments
                        evaluated = line.replace("Model:", "")
                        models.append(evaluated)
                        continue
                    if line.startswith("Semantics:"):
                        continue
            calc_results.close()
    return (len(models)),(len(set(models)))

# search for duplicates in the calculated models
def countModels(min,max,semantics):
    for nodesize in range(min,max+1):
        proxy_expr = r"Eval.*Nodes_"+str(nodesize) + "_"
        # do not load tri evaluation
        two_expr = proxy_expr + r".*Sem_(?!.*tri).*" +  ",".join(semantics)
        two_expr = re.compile(two_expr)
        twoRes = modelCounter(nodesize,two_expr)

        # load tri evaluation
        tri_expr = proxy_expr + r".*Sem_(?=.*tri).*"  +  ",".join(semantics)
        tri_expr = re.compile(tri_expr)
        triRes = modelCounter(nodesize, tri_expr)

        print("NodeSize:{} Semantics:{}".format(nodesize,semantics))
        # print how many models have been found and how many models are unique
        print("TwoValued NbrModels:{} - NbrUnique:{}".format(twoRes[0],twoRes[1]))
        print("TriValued NbrModels:{} - NbrUnique:{}".format(triRes[0],triRes[1]))

# check models from node size 1 to 8 for admissible interpreation
countModels(1,8,["a"])

# create a plot, min and max are specifying the node size range; sem1,sem2 are specify the semantics which shall be plotted;
# sem1note; sem2note are specifying the description of the used semantics in the legend
def plot_gain(min,max,sem1,sem2,sem1note,sem2note):
    # collect two and three-valued data for sem1
    sem1_final = []
    for nbrNodes in range(min,max+1):
        result = get_results(nbrNodes, sem1)
        sem1_final.append(result)
    sem_nodes_1 = list(map( lambda  x: x[0],sem1_final))
    class_time_1 = list(map( lambda  x: x[1],sem1_final))
    tri_time_1 = list(map( lambda  x: x[2],sem1_final))

    # collect two and three-valued data for sem2
    sem2_final = []
    for nbrNodes in range(min, max + 1):
        result = get_results(nbrNodes, sem2)
        sem2_final.append(result)
    sem_nodes_2 = list(map(lambda x: x[0], sem2_final))
    class_time_2 = list(map(lambda x: x[1], sem2_final))
    tri_time_2 = list(map(lambda x: x[2], sem2_final))

    #create a plot
    font = {'family': 'normal',
            'weight': 'normal',
            'size': 50}

    plt.rc('font', **font)
    fig, ax = plt.subplots()

    ax.plot(sem_nodes_1,class_time_1,label=sem1note+"-two",linewidth=3,color ="b", linestyle="-")
    ax.plot(sem_nodes_1,tri_time_1,label= sem1note + "-tri",linewidth=3,color ="b",linestyle="dotted")
    ax.plot(sem_nodes_2,class_time_2,label= sem2note +"-two",linewidth=3,color ="r", linestyle="-")
    ax.plot(sem_nodes_2,tri_time_2,label=sem2note+"-tri",linewidth=3,color ="r",linestyle="dotted")

    ax.set_ylabel('Time in Seconds',fontsize="medium")
    ax.set_xlabel('Number of Statements',fontsize="medium")
    ax.set_aspect('equal', adjustable='box')
    plt.yscale("log")
    plt.legend(loc='best')
    ax.legend(loc='upper left')
    fig.tight_layout()
    #ax.yaxis(fontsize="medium")
    ax.set_xlim(xmin=1, xmax=len(sem_nodes_1))
    plt.xticks([x for x in range(1,9)])
    #ax.set_title('Comparison of Admissible and Complete Semantics',fontsize="medium")
    plt.show()


# collect data which is needed in order to create a table, the semantics variable specifies the used semantics
# the nodenbr in range specifes the range of node sizes included in the table
# for a specified semantics we collect the avg time of the two-valued completion, the three-valued logic one and calculate the speed factor, indicating how much faster the latter approach is
def tablecontent_creator():
    #semantics = [["a"],["c"],["p"]
    semantics = [["a"],["c"]]

    # create head
    table_head = ["Size"]
    for singSem in semantics:
        table_head += ["{}".format(singSem), "tri-{}".format(singSem), "Speed"]
    final_table = [table_head]

    # create body
    for nodenbr in range(1,9):
        table_row = [nodenbr]
        for singSem in semantics:
            nbr,two,tri = get_results(nodenbr,singSem)
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


#mult_html_writer(tablecontent_creator())
mult_tex_writer(tablecontent_creator())
plot_gain(1,8,["a"],["c"],"adm","cmp")


