from rdf_store import Rdf_store


class Helper:
    xmlRdfQuery = ""
    int1 = ""
    depth = 0
    r = Rdf_store()

    def getXMLValue(self, listValues):
        for node in listValues:
            return node.firstChild.nodeValue

    def getMaxValue(self, listValues):
        maxValue = 0
        self.depth = 0
        for node in listValues:
            self.int1 = ""
            nodeVal = self.extractInt(node.firstChild.nodeValue)
            if nodeVal > maxValue:
                maxValue = nodeVal

        return maxValue

    def extractInt(self, value):
        charsToCheck = value[len(value) - 1:]
        if charsToCheck.isdigit():
            self.int1 = charsToCheck + self.int1
            offset = len(value) - 1
            charsLeft = value[:offset]
            self.extractInt(charsLeft)

        return int(self.int1)

    def hasDuplicate(self, query):
        if self.getXMLValue(self.r.parseXMLResult(self.r.queryBigData(query))) is None:
            return 0
        else:
            return 1

    def indentText(self, indent, text):
        string = ""
        for x in range(0, indent):
            string += str("  ")
        string += text
        return string
