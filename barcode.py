import cairo
from optparse import OptionParser

def cmToPoints( x ) :
    return x * 72 / 2.54

pageA4WidthInPoints = cmToPoints( 21.0 )
pageA4HeightInPoints = cmToPoints( 29.7 )

##############################################################################################################

class Barcode( object ) :
    def __init__( self ) : 
        pass

    def insertSpacesIntoText( self, text, distance = 2 ) :
        textWithSpace = ""
        i = 0
        textLength = len( text )
        while i < textLength :
            if i != 0 and i % distance == 0 : 
                textWithSpace += " "
            textWithSpace += text[ i ]
            i += 1
        # print "spaces into text: '%s'" % textWithSpace 
        return textWithSpace

##############################################################################################################

class BarcodeITF( Barcode ) :
    encodingList = [
        "11331",
        "31113",
        "13113",
        "33111",
        "11313",
        "31311",
        "13311",
        "11133",
        "31131",
        "13131",
        "1111", # start
        "311"  # stop
    ]

    def __init__( self ) :
        Barcode.__init__( self )

    def encodeSymbolPair( self, c1, c2 ) :
        symbolEncoding1 = self.encodingList[ c1 ]
        symbolEncoding2 = self.encodingList[ c2 ]
        # print "c: %s %s" % ( c, symbolEncoding )
        symbolEncodingLength = len( symbolEncoding1 )
        symbolEncoding = ""
        i = 0
        while i < symbolEncodingLength :
            symbolEncoding += symbolEncoding1[ i ] + symbolEncoding2[ i ] 
            i += 1
        return symbolEncoding 

    def internalEncode( self, symbols ) :
        encoding = ""
        encoding +=  self.encodingList[ 10 ]  # start 
        i = 0
        symbolsLength = len( symbols )
        while i < symbolsLength :
            c1 = symbols[ i ]
            i += 1
            c2 = symbols[ i ]
            i += 1
            encoding += self.encodeSymbolPair( c1, c2 )
        encoding += self.encodingList[ 11 ] # stop
        return encoding

    def partitionBase10( self, inputText, withChecksum = False ) :
        symbols = []
        text = ""
        checksum = 0
        inputTextEven = ( len( inputText ) % 2 == 0 )
        if ( withChecksum and inputTextEven ) or ( not withChecksum and not inputTextEven ) :
            inputText = "0" + inputText
        ord0 = ord( "0" )
        i = 0
        for c in inputText :
            x = ord( c ) - ord0
            if x < 0 or x > 9 : 
                x = 0
                c = "0"
            text += c 
            symbols.append( x )
            if i % 2 == 0 :
                checksum += 3 * x
            else:
                checksum += 1 * x
            i += 1
        checksum = ( 10 - ( checksum % 10 ) ) % 10
        if withChecksum : 
            text += "%s" % checksum
            symbols.append( checksum )
        return self.insertSpacesIntoText( text ), symbols

    def encode( self, inputText ) :
        # replace all non number symbols with 0 padd left if necessary and compute checksum
        text, symbols = self.partitionBase10( inputText )
        return text, self.internalEncode( symbols )


##############################################################################################################

class Barcode128( Barcode ) :
    encodingList = [
        "212222",
        "222122",
        "222221",
        "121223",
        "121322",
        "131222",
        "122213",
        "122312",
        "132212",
        "221213",
        "221312",
        "231212",
        "112232",
        "122132",
        "122231",
        "113222",
        "123122",
        "123221",
        "223211",
        "221132",
        "221231",
        "213212",
        "223112",
        "312131",
        "311222",
        "321122",
        "321221",
        "312212",
        "322112",
        "322211",
        "212123",
        "212321",
        "232121",
        "111323",
        "131123",
        "131321",
        "112313",
        "132113",
        "132311",
        "211313",
        "231113",
        "231311",
        "112133",
        "112331",
        "132131",
        "113123",
        "113321",
        "133121",
        "313121",
        "211331",
        "231131",
        "213113",
        "213311",
        "213131",
        "311123",
        "311321",
        "331121",
        "312113",
        "312311",
        "332111",
        "314111",
        "221411",
        "431111",
        "111224",
        "111422",
        "121124",
        "121421",
        "141122",
        "141221",
        "112214",
        "112412",
        "122114",
        "122411",
        "142112",
        "142211",
        "241211",
        "221114",
        "413111",
        "241112",
        "134111",
        "111242",
        "121142",
        "121241",
        "114212",
        "124112",
        "124211",
        "411212",
        "421112",
        "421211",
        "212141",
        "214121",
        "412121",
        "111143",
        "111341",
        "131141",
        "114113",
        "114311",
        "411113",
        "411311",
        "113141",
        "114131",
        "311141",
        "411131",
        "211412",
        "211214",
        "211232", # das ist das Startzeichen
        "2331112" # Stopzeichen
    ]

    def __init__( self ) : 
        Barcode.__init__( self )

    def internalEncode( self, symbols, startSymbol = 105 ) :
        moduloSum = 0
        encoding = ""
        encoding += self.encodingList[ startSymbol ] 
        moduloSum += startSymbol
        positionCounter = 1
        for c in symbols : 
            moduloSum += c * positionCounter
            positionCounter += 1
            encoding += self.encodingList[ c ] 
        checkSum = moduloSum % 103
        encoding += self.encodingList[ checkSum ] 
        encoding += self.encodingList[ 106 ] 
        return encoding


    def convertInputNumbersToSymbols( self, inputText ) :
        if len( inputText ) % 2 == 1:
            inputText = "0" + inputText
        symbols = []
        inputTextLength = len( inputText )
        i = 0
        ord0 = ord( "0" )
        while i < inputTextLength :
            x1 = ord( inputText[ i ] ) - ord0
            i += 1
            x2 = ord( inputText[ i ] ) - ord0
            i += 1
            x = x1 * 10 + x2
            symbols.append( x )
        return self.insertSpacesIntoText( inputText ), symbols

    def convertInputTextToSymbols( self, inputText ) :
        symbols = []
        for c in inputText :
            ordC = ord( c )
            if ordC >= 32 and ordC <=126 : 
                symbols.append( ordC - 32 )
        return self.insertSpacesIntoText( inputText ), symbols
                
    def checkIfOnlyNumbers( self, inputText ) :
        ord0 = ord( "0" )
        for c in inputText :
            x = ord( c ) - ord0
            if x < 0 or x > 9 :
                return False
        return True

    def encode( self, inputText ) :
        if self.checkIfOnlyNumbers( inputText ) :
            text, symbols = self.convertInputNumbersToSymbols( inputText )
            return text, self.internalEncode( symbols, 105 )
        else:
            text, symbols = self.convertInputTextToSymbols( inputText )
            return text, self.internalEncode( symbols, 104 )


##############################################################################################################

class Barcode39( Barcode ) :
    encodingMap = {
        "0" :  "1113313111",
        "1" :  "3113111131",
        "2" :  "1133111131",
        "3" :  "3133111111",
        "4" :  "1113311131",
        "5" :  "3113311111",
        "6" :  "1133311111",
        "7" :  "1113113131",
        "8" :  "3113113111",
        "9" :  "1133113111",
        "A" :  "3111131131",
        "B" :  "1131131131",
        "C" :  "3131131111",
        "D" :  "1111331131",
        "E" :  "3111331111",
        "F" :  "1131331111",
        "G" :  "1111133131",
        "H" :  "3111133111",
        "I" :  "1131133111",
        "J" :  "1111333111",
        "K" :  "3111111331",
        "L" :  "1131111331",
        "M" :  "3131111311",
        "N" :  "1111311331",
        "O" :  "3111311311",
        "P" :  "1131311311",
        "Q" :  "1111113331",
        "R" :  "3111113311",
        "S" :  "1131113311",
        "T" :  "1111313311",
        "U" :  "3311111131",
        "V" :  "1331111131",
        "W" :  "3331111111",
        "X" :  "1311311131",
        "Y" :  "3311311111",
        "Z" :  "1331311111",
        "-" :  "1311113131",
        "." :  "3311113111",
        " " :  "1331113111",
        "$" :  "1313131111",
        "/" :  "1313111311",
        "+" :  "1311131311",
        "%" :  "1113131311",
        "*" :  "1311313111" }
    
    def __init__( self ) : 
        Barcode.__init__( self )


    def internalEncode( self, text ) :
        encoding = ""
        for c in text : 
            encoding += self.encodingMap[ c ]
        return encoding

    def encode( self, text ) :
        return text, self.internalEncode( "*%s*" % text )

##############################################################################################################

class Label( object ) : 
    barWidth = 1.0 # 0.8
    barHeight = cmToPoints( 1.0 )
    withChecksum = True

    def __init__( self, cairoContext, labelSheet, options ) :
        self.options = options
        self.withBorderLines = options.withBorderLines
        self.labelTitle = options.labelTitle
        self.labelSheet = labelSheet
        self.ctx = cairoContext
        self.ctx.set_line_width( 1 )
        self.ctx.set_source_rgb( 0, 0, 0 )
        self.barcodeRendererList = []
        self.barcodeRendererList.append( Barcode128() )
        # self.barcodeRendererList.append( BarcodeITF() )
        # self.barcodeRendererList.append( Barcode39() )
        self.barcodeRendererCounter = 0

    def showText( self, x, y, text, textSize = 10, align = "center" ) :
        self.ctx.set_font_size( textSize )
        txBearing, tyBearing, tWidth, tHeight, txAdvance, tyAdvance = self.ctx.text_extents( text ) 
        textX = x
        if align == "center" :
            textX = x - txAdvance / 2
        elif align == "right" :
            textX = x - txAdvance
        self.ctx.move_to( textX, y )
        self.ctx.show_text( text )
        return textX + txAdvance
    
    def drawBar( self, x, y, isBlack, width ) :
        if isBlack: 
            x1 = x + width / 2.0
            self.ctx.move_to( x1, y )
            self.ctx.line_to( x1, y + self.barHeight )
            self.ctx.set_line_width( width )
            self.ctx.stroke()
        else :
            width = width + 0.2
        return x + width, y 

    def drawSymbolEncoding( self, x, y, symbolEncoding ) :
        isBlack = True
        for barC in symbolEncoding :
            barWidth = self.barWidth * ( ord( barC ) - ord( '0' ) )
            x, y = self.drawBar( x, y, isBlack, barWidth )
            isBlack = not isBlack
        return x, y

    def symbolExtent( self, symbolEncoding ) :
        isBlack = True
        symbolWidth = 0
        for barC in symbolEncoding :
            symbolWidth += self.barWidth * ( ord( barC ) - ord( '0' ) )
            if not isBlack :
                symbolWidth += 0.2
            isBlack = not isBlack
        return symbolWidth

        
    def drawBarcode( self, centerX, centerY, text, barcodeRenderer = None, labelNote = None  ) : 
        if not barcodeRenderer :
            barcodeRenderer = self.barcodeRendererList[ self.barcodeRendererCounter ]
            self.barcodeRendererCounter = ( self.barcodeRendererCounter + 1 ) % len( self.barcodeRendererList )
        text, encoding = barcodeRenderer.encode( text )
        symbolExtent = self.symbolExtent( encoding )
        self.drawSymbolEncoding( centerX - symbolExtent / 2, centerY - self.barHeight / 2, encoding )
        textY = centerY + self.barHeight / 2 + cmToPoints( 0.4 )
        textEndX = self.showText( centerX, textY, text )
        if labelNote :
            self.showText( textEndX + cmToPoints( 0.4 ), textY, labelNote, 5, align = "left" )


    def drawBorders( self, x, y ) :
        if not self.withBorderLines :
            return
        self.ctx.set_line_width( 0.1 )
        x1 = x + 0.05
        x2 = x + self.labelSheet[ "labelWidth" ] - 0.05
        y1 = y + 0.05
        y2 = y + self.labelSheet[ "labelHeight" ] - 0.05
        self.ctx.move_to( x1, y1 )
        self.ctx.line_to( x2, y1 )
        self.ctx.line_to( x2, y2 )
        self.ctx.line_to( x1, y2 )
        self.ctx.line_to( x1, y1 )
        self.ctx.close_path()
        self.ctx.stroke()


    def drawDestinationDescription( self, text ) :
        self.showText( cmToPoints( 1 ), self.labelSheet[ "offsetY" ] - 12, text, 12, align= "left" )


    def drawLabelTitle( self, centerX, y ) :
        # centerX, centerY is the center of the text, not the center of the label
        self.showText( centerX, y + cmToPoints( 0.5 ), self.labelTitle, textSize = 8 )


    def drawLabel( self, x, y, text, labelNote = None ) : 
        # x, y is the upper left corner, the axis extends to right and down 
        self.drawBorders( x, y )
        centerX = x + self.labelSheet[ "labelWidth" ] / 2
        centerY = y + self.labelSheet[ "labelHeight" ] / 2
        self.drawLabelTitle( centerX, centerY - self.barHeight - cmToPoints( 0.3 ) )
        self.drawBarcode( centerX, centerY, text, labelNote = labelNote )


    def drawPageWithLabelsList( self, destinationDescription, labels ) :
        if not labels or len( labels ) == 0 :
            return 
        self.drawDestinationDescription( destinationDescription )
        labelsLength = len( labels )
        labelsCounter = 0
        x = self.labelSheet[ "offsetX" ]
        for itX in range( 0, self.labelSheet[ "columns" ] ) :
            y = self.labelSheet[ "offsetY" ]
            for itY in range( 0, self.labelSheet[ "rows" ] ) :
                label = labels[ labelsCounter ]
                labelSplit = label.split( "*" )
                labelText = labelSplit[ 0 ]
                labelNote = ""
                if len( labelSplit ) > 1 : 
                    labelNote = labelSplit[ 1 ]
                print "drawLabel '%s': %7.2f, %7.2f" % ( labelText, x ,y )
                self.drawLabel( x, y, labelText, labelNote ) 
                labelsCounter = ( labelsCounter + 1 ) % labelsLength
                self.ctx.stroke()
                if labelsCounter == 0 : 
                    return
                y += self.labelSheet[ "labelHeight" ] + self.labelSheet[ "interLabelY" ]
            x += self.labelSheet[ "labelWidth" ] + self.labelSheet[ "interLabelX" ]


    def drawPageWithCounter( self, destinationDescription, counter = 0 ) :
        self.drawDestinationDescription( destinationDescription )
        x = self.labelSheet[ "offsetX" ]
        for itX in range( 0, self.labelSheet[ "columns" ] ) :
           y = self.labelSheet[ "offsetY" ] 
           for itY in range( 0, self.labelSheet[ "rows" ] ) :
                labelText = "%s" % counter
                print "drawLabel '%s': %7.2f, %7.2f" % ( labelText, x ,y )
                self.drawLabel( x, y, labelText ) 
                self.ctx.stroke()
                counter += 1
                y += self.labelSheet[ "labelHeight" ] + self.labelSheet[ "interLabelY" ]
           x += self.labelSheet[ "labelWidth" ] + self.labelSheet[ "interLabelX" ]

    def drawPage( self ):
        labelsTextList = None
        if self.options.labelsConcaternated :
            labelsTextList = self.options.labelsConcaternated.split( ";" )
            print "size of labelsTextList: %s" % len( labelsTextList )

        if labelsTextList and len( labelsTextList ) != 0 :
            self.drawPageWithLabelsList( self.options.description, labelsTextList )
        else:
            self.drawPageWithCounter( self.options.description, self.options.counter )

##############################################################################################################

labelSheetDefinitions = {
   "test" : {
       "name" : "Test48.5 x 25.4 40 Labels",
       "labelWidth" : cmToPoints( 4.85 ),
       "labelHeight" : cmToPoints( 2.54 ),
       "interLabelX" : cmToPoints( 0.00 ),
       "interLabelY" : cmToPoints( 0.00 ),
       "offsetX" : cmToPoints( 0.80 ),
       "offsetY" : cmToPoints( 2.15 ),
       "rows" : 1,
       "columns" : 1
   },
   
   "avery8160" : {
       "name" : "Avery 8160 63.5 x 38.1 21 Labels",
       "labelWidth" : cmToPoints( 6.35 ),
       "labelHeight" : cmToPoints( 3.81 ),
       "interLabelX" : cmToPoints( 0.25 ),
       "interLabelY" : cmToPoints( 0.00 ),
       "offsetX" : cmToPoints( 0.70 ),
       "offsetY" : cmToPoints( 1.55 ),
       "rows" : 7,
       "columns" : 3
   },
   
   "avery4780" : {
       "name" : "Avery 4780 48.5 x 25.4 40 Labels",
       "labelWidth" : cmToPoints( 4.85 ),
       "labelHeight" : cmToPoints( 2.54 ),
       "interLabelX" : cmToPoints( 0.0 ),
       "interLabelY" : cmToPoints( 0.0 ),
       "offsetX" : cmToPoints( 0.8 ),
       "offsetY" : cmToPoints( 2.15 ),
       "rows" : 10,
       "columns" : 4
   },
   
   "avery3490" : {
       "name" : "Avery 3490 70.0 x 36.0 24 Labels",
       "labelWidth" : cmToPoints( 7.00 ),
       "labelHeight" : cmToPoints( 3.60 ),
       "interLabelX" : cmToPoints( 0 ),
       "interLabelY" : cmToPoints( 0 ),
       "offsetX" : cmToPoints( 0.0 ),
       "offsetY" : cmToPoints( 0.4 ),
       "rows" : 8,
       "columns" : 3
   }
}

##############################################################################################################

def parseCommandLineOptions() :
    parser = OptionParser()
    parser.add_option( "--fileName", dest="fileName", type = "string", default = "barcode.pdf" )
    parser.add_option( "--description", dest="description", type = "string", default = "" )
    parser.add_option( "--labels", dest="labelsConcaternated", type="string", default = "" )
    parser.add_option( "--labelSheet", dest="labelSheet", type="string", default = "avery4780" )
    parser.add_option( "--labelTitle", dest="labelTitle", type="string", default = "Bibliothek KGS Forster Linde" )
    parser.add_option( "--withBorderLines", dest="withBorderLines", action="store_true", default = False )
    parser.add_option( "--counter", dest="counter", type="int", default = 0 )
    return parser.parse_args()

def generateLabels( destinationFile, labelSheet, options ) :
    pdfSurface = cairo.PDFSurface( destinationFile, pageA4WidthInPoints, pageA4HeightInPoints )
    cairoContext = cairo.Context( pdfSurface )
    label = Label( cairoContext, labelSheet, options )
    label.drawPage()
    pdfSurface.finish()


def main() :
    options, args = parseCommandLineOptions()
    
    labelSheetName = options.labelSheet
    labelSheet = None 
    if labelSheetName in labelSheetDefinitions : 
        labelSheet = labelSheetDefinitions[ labelSheetName ]
    else:
        raise Exception( "label sheet unknown '%s'" % labelSheetName )
    print "labelSheet: '%s'" % labelSheetName
    
    destinationFile = open( options.fileName, "w" )
    generateLabels( destinationFile, labelSheet, options )
    destinationFile.close()

main()
