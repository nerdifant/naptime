class Message:
    def __init__ ( self ):
        self.log = []
        self.log_err = []
        self.verbose = False

    def __print__( self, text, show, color= '', error=False ):
        if show or (self.verbose and not show):
            print(color + text + '\033[0m')
            self.log.append(color + text + '\033[0m')
            if error:
                self.log_err.append(color + text + '\033[0m')

    def setVerbose( self):
        self.verbose = True

    def rt ( self, text, show=True ): self.__print__( text, show, '\033[91m', True )
    def gn ( self, text, show=True ): self.__print__( text, show, '\033[92m' )
    def ge ( self, text, show=True ): self.__print__( text, show, '\033[93m' )
    def bl ( self, text, show=True ): self.__print__( text, show, '\033[94m' )
    def vi ( self, text, show=True ): self.__print__( text, show, '\033[95m' )
    def ws ( self, text, show=True ): self.__print__( text, show )

    def out( self ):
        for string in self.log:
            text = text + string + '\n'
        return text

    def err( self ):
        for string in self.log_err:
            text = text + '\n' + string
        return text
