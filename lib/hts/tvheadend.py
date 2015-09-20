#!/usr/bin/env python
#
# Copyright (C) 2012 Adam Sutton <dev@adamsutton.me.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
This is a very simple HTSP client library written in python mainly just
for demonstration purposes.

Much of the code is pretty rough, but might help people get started
with communicating with HTSP server
"""

import urllib2
import json
import htsmsg
import log

# ###########################################################################
# HTSP Client
# ###########################################################################

HTSP_PROTO_VERSION = 6

# Create passwd digest
def htsp_digest ( user, passwd, chal ):
  import hashlib
  ret = hashlib.sha1(passwd + chal).digest()
  return ret

# Client object
class client:

  ## ----- Setup connection
  def __init__ ( self, addr, name = 'HTSP PyClient' ):
    import socket

    # Setup for TVheadend API
    self._host = addr[0]
    self._port = addr.pop(1)

    # Setup for HTSP Client
    self._sock = socket.create_connection(addr)
    self._name = name
    self._auth = None
    self._user = None
    self._pass = None

  # Send
  def send ( self, func, args = {} ):
    args['method'] = func
    if self._user: args['username'] = self._user
    if self._pass: args['digest']   = htsmsg.hmf_bin(self._pass)
    log.debug('htsp tx:')
    log.debug(args, pretty=True)
    self._sock.send(htsmsg.serialize(args))

  # Receive
  def recv ( self ):
    ret = htsmsg.deserialize(self._sock, False)
    log.debug('htsp rx:')
    log.debug(ret, pretty=True)
    return ret

  # Setup
  def hello ( self ):
    args = {
      'htspversion' : HTSP_PROTO_VERSION,
      'clientname'  : self._name
    }
    self.send('hello', args)
    resp = self.recv()

    # Store
    self._version = min(HTSP_PROTO_VERSION, resp['htspversion'])
    self._auth    = resp['challenge']
    
    # Return response
    return resp

  # Authenticate
  def authenticate ( self, user, passwd = None ):
    self._user = user
    if passwd:
      self._pass = htsp_digest(user, passwd, self._auth)
    self.send('authenticate')
    resp = self.recv()
    if 'noaccess' in resp:
      raise Exception('Authentication failed')

  # Enable async receive
  def enableAsyncMetadata ( self, args = {} ):
    self.send('enableAsyncMetadata', args)


  ## ----- Request information about a set of events. If no options are specified the entire EPG database will be returned.
  def getEvents ( self, eventId = None, channelId = None, numFollowing = None, maxTime = None, language = None ):

    args = {}
    if eventId: args['eventId'] = eventId
    if channelId: args['channelId'] = channelId
    if numFollowing: args['numFollowing'] = numFollowing
    if maxTime: args['maxTime'] = maxTime
    if language: args['language'] = language

    self.send('getEvents', args)
    resp = self.recv()

    # Return response
    return resp

    
  ## ----- Get EPG Grid
  def epgGetGrid ( self, start = None, limit = None ):
    url = "http://" + self._host + ":" + str( self._port ) + "/api/epg/events/grid?"

    if start: url = url + "start=" + str(start) + "&"
    if limit: url = url + "limit=" + str(limit) + "&"

    resp = urllib2.urlopen(url).read()
    resp = json.loads(resp)

    # Return response
    return resp


  ## ----- Query the EPG (event titles) and optionally restrict to channel/tag/content type.
  def epgQuery ( self, query, channelId = None, tagId = None, contentType = None, minduration = None, maxduration = None, language = None, full = 0 ):

    args = {
      'query': query,
      'full': full
    }

    if channelId: args['channelId'] = channelId
    if tagId: args['tagId'] = tagId
    if contentType: args['contentType'] = contentType
    if minduration: args['minduration'] = minduration
    if maxduration: args['maxduration'] = maxduration
    if language: args['language'] = language

    self.send('epgQuery', args)
    resp = self.recv()

    # Return response
    return resp


  ## ----- Return a list of DVR configurations.
  def dvrGetConfigs ( self, dvrconfigs = None ):
    
    args = {}
    if dvrconfigs: args['dvrconfigs'] = dvrconfigs

    self.send('getDvrConfigs', args)
    resp = self.recv()

    # Return response
    return resp


  ## ----- Get Grid of Recordings ( upcoming, finished, failed )
  def dvrGetGrid ( self, grid = "upcoming", start = None, limit = None, sort = False ):
    url = "http://" + self._host + ":" + str( self._port ) + "/api/dvr/entry/grid_" + grid + "?"

    if start: url = url + "start=" + str(start) + "&"
    if limit: url = url + "limit=" + str(limit) + "&"
    if sort: url = url + "sort=start_real&"

    resp = urllib2.urlopen(url).read()
    resp = json.loads(resp)

    # Return response
    return resp


# ############################################################################
# Editor Configuration
#
# vim:sts=2:ts=2:sw=2:et
# autocmd Filetype python setlocal ts=2 sts=2 sw=2 expandtab
# ############################################################################
