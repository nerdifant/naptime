## ----- Colors
def rt ( text ): print '\033[91m' + text + '\033[0m'
def gn ( text ): print '\033[92m' + text + '\033[0m'
def ge ( text ): print '\033[93m' + text + '\033[0m'
def bl ( text ): print '\033[94m' + text + '\033[0m'
def vi ( text ): print '\033[95m' + text + '\033[0m'


class message:
  def __init__ ( self, verbose ):
    self.log = []
    self.log_err = []
    self.verbose = verbose

  def rt ( self, text ):
    text = '\033[91m' + text + '\033[0m'
    text = text.encode("utf-8") 
    self.log.append(text)
    self.log_err.append(text)
    print text

  def gn ( self, text ):
    text = '\033[92m' + text + '\033[0m'
    text = text.encode("utf-8") 
    self.log.append(text)
    print text

  def ge ( self, text ):
    text = '\033[93m' + text + '\033[0m'
    text = text.encode("utf-8") 
    self.log.append(text)
    print text

  def bl ( self, text ):
    text = '\033[94m' + text + '\033[0m'
    text = text.encode("utf-8") 
    self.log.append(text)
    print text

  def vi ( self, text ):
    text = '\033[95m' + text + '\033[0m'
    text = text.encode("utf-8") 
    self.log.append(text)
    print text

  def ws ( self, text ):
    text = text.encode("utf-8") 
    self.log.append(text)
    print text

  def v ( self, text ):
    text = text.encode("utf-8") 
    self.log.append(text)
    if self.verbose:
      print text

  def out( self ):
    text = ''
    for string in self.log:
      text = text + string + '\n'
    return text

  def err( self ):
    text = ''
    for string in self.log_err:
      text = text + '\n' + string
    return text
