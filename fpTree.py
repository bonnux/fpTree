#coding=utf-8
import fpTree

#定义一个树，保存树的每一个结点
class treeNode:
    def __init__(self,nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.parent = parentNode
        self.children = {}   #用于存放节点的子节点
        self.nodeLink = None #用于连接相似的元素项
    
    #对count变量增加给定值
    def inc(self, numOccur):
        self.count += numOccur

#创建fp树
def createTree(dataSet, minSup):
    # 遍历数据集，统计各元素项出现次数，创建头指针表
    headerTable = {}
    for line in dataSet:
        for item in line:
            headerTable[item] = headerTable.get(item, 0) + dataSet[line]
    # 删除头指针表中不满足最小支持度的项
    for i in headerTable.keys():
        if headerTable[i] < minSup:
            del(headerTable[i])
    # 空元素集，返回空
    freqItemSet = set(headerTable.keys())
    if len(freqItemSet) == 0:
        return None, None
    # 增加一个数据项，用于存放指向相似元素项指针
    for j in headerTable:
        headerTable[j] = [headerTable[j], None]
    retTree = treeNode('Null Set', 1, None) # 根节点

    # 再次遍历经过筛选的数据集，创建fp树
    for tranSet, count in dataSet.items():
        localD = {}    # 对一个项集，记录其中每个元素项在数据集中的频数
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)] # 排序
            updateTree(orderedItems, retTree, headerTable, count) # 更新fp树
    return retTree, headerTable

def updateTree(items, inTree, headerTable,count):
    #判断事务中的第一个元素项是否作为子节点存在，如果存在则更新该元素项的计数
    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count)
    #如果不存在，则创建一个新的子节点添加到树中
    else:
        inTree.children[items[0]] = treeNode(items[0],count,inTree)
        # 更新头指针表或前一个相似元素项节点的指针指向新节点
        if headerTable[items[0]][1]==None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1],inTree.children[items[0]])
     # 对剩下的元素项递归调用本函数
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)    

#获取头指针表中该元素项对应的单链表的尾节点，然后将其指向新节点targetNode            
def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode   

def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict

#给定元素项生成一个条件模式基
def findPrefixPath(basePat,treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []     
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

#辅助函数，直接修改prefixPath的值，将当前节点leafNode添加到prefixPath的末尾，然后递归添加其父节点
def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)    

#递归查找频繁项集
def mineTree(inTree,headerTable,minSup,preFix,freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(),key = lambda p:p[1])]
    for basePat in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        myConTree,myHead = createTree(condPattBases, minSup)
        
        if myHead != None:
            mineTree(myConTree, myHead, minSup, newFreqSet, freqItemList)

if __name__ == "__main__":
    # 最小支持度
    minSup = 500

    # 将数据集加载到列表
    parsedDat = [line.split() for line in open('data.txt').readlines()]

    # 初始集合格式化
    initSet = fpTree.createInitSet(parsedDat)

    # 构建FP树
    myFPtree, myHeaderTab = fpTree.createTree(initSet, minSup)

    # 创建空列表，保存频繁项集
    myFreqList = []
    fpTree.mineTree(myFPtree, myHeaderTab, minSup, set([]), myFreqList)
    print "频繁项集个数：", len(myFreqList)
    print "频繁项集：",myFreqList