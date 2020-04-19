# -*- coding: utf-8 -*-
import json
import re
import xml.etree.ElementTree as ET
import requests

class parser:
	def __init__(self):
		self.result = {'items':[],'pagination':{'currentPage':0}}
	"""
	def parseShows(url='http://www.mdr.de/mediathek/fernsehen/a-z/sendungenabisz100-meta.xml'):
		response = libMediathek.getUrl(url)
		root = ET.fromstring(response)
		i = 0
		l = []
		#document,childNodes,childNode,childNodes,properties,propertie#2,document,customElements,queryResult
		#n = root.find('childNodes').find('childNode').find('childNodes').find('childNode').find('properties')[0]
		children = root.find('childNodes')
		for child in children:
			if child.attrib['nodeType'] == 'mdr-core-nt:boxMultiGroupStandard':
				children2 = child.find('childNodes')
				for child2 in children2:
					if child2.attrib['nodeType'] == 'mdr-core-nt:customTeaserFilterRef':
						documents = child2.find('properties')[1].find('document').find('customElements').find('queryResult')
						
		for document in documents:
			d = {}
			for node in document:
				if node.tag == 'properties':
					for node2 in node:
						if node2.attrib.get('name','') == 'mdr-core:teaserText':
							try:
								if node2[0].text != None:
									d['_plot'] = node2[0].text
							except: pass
						elif node2.attrib.get('name','') == 'mdr-core:headline':
							try:
								d['_name'] = node2[0].text
							except: pass
					i = 1	
				elif node.tag == 'childNodes':
					for node2 in node:
						if node2.attrib.get('name','') == 'mdr-core:teaserImage':
							d['_thumb'] = _getThumb(node2)
						
				elif node.tag == 'customElements':
					for node2 in node:
						if node2.tag == 'metaxmlUrl':
							d['url'] = node2.text
			d['_type'] = 'dir'
			d['mode'] = 'libMdrListVideos'
			d['_channel'] = 'MDR'
			if d['_name'] != 'LexiTV':#lexitv returns an error with this api - ignore it for now
				l.append(d)
		return l
	"""

	def parseVideos(self,url='http://www.mdr.de/tv/programm/mordenimnorden100-meta.xml'):
		response = requests.get(url).text
		root = ET.fromstring(response)
		
		l = []
		#document,broadcasts,broadcast,
		for broadcast in root[0]:
			d = {'type':'video', 'params':{'mode':'libMdrPlay'}, 'metadata':{'art':{}}}
			for node in broadcast[0]:
				if node.tag == 'videos':
					d['params']['url'] = node[0][0][0][1].text#todo: makemrobust
				elif node.tag == 'properties':
					for node2 in node:#mdr-core:episodeText
						if node2.attrib.get('name','') == 'mdr-core:episodeText':
							d['metadata']['name'] = node2[0].text
						if node2.attrib.get('name','') == 'mdr-core:broadcastSeriesTitle':
							d['metadata']['tvshowtitle'] = node2[0].text
						if node2.attrib.get('name','') == 'mdr-core:headline':
							if not '_name' in d:
								d['metadata']['name'] = node2[0].text
							if not '_tvshowtitle' in d:
								d['metadata']['tvshowtitle'] = node2[0].text
						if node2.attrib.get('name','') == 'mdr-core:fsk':
							d['metadata']['mpaa'] = node2[0].text
						if node2.attrib.get('name','') == 'mdr-core:language':
							d['metadata']['lang'] = node2[0].text
						if node2.attrib.get('name','') == 'mdr-core:episodeNumber':
							d['metadata']['episode'] = node2[0].text
						if node2.attrib.get('name','') == 'mdr-core:duration':
							s = node2[0].text.split(':')
							d['metadata']['duration'] = str(int(s[0]) * 3600 + int(s[1]) * 60 + int(s[2]))
				elif node.tag == 'childNodes':
					for node2 in node:
						if node2.attrib.get('name','') == 'mdr-core:teaserImage':
							try:
								d['metadata']['art']['thumb'] = _getThumb(node2)
								#for node3 in node2[0]:
								#	if node3.attrib.get('name','') == 'sophora:reference':
								#		d['thumb'] = node3[1][0][0].text.replace('.html','-resimage_v-variantBig16x9_w-960.png?version=4333')
							except: pass
						elif node2.attrib.get('name','') == 'mdr-core:copyText':
							try:
								for node3 in node2:
									if node3.tag == 'childNodes':
										for property in node3[0][0]:
											if property.attrib.get('name','') == 'sophora-extension:text':
												if property[0].text is not None:
													d['metadata']['plot'] = property[0].text.replace('<br/>','\n')
							except: pass
			self.result['items'].append(d)
		return self.result
	"""
		
	def parseDays(url='http://www.mdr.de/mediathek/fernsehen/sendung-verpasst--100-meta.xml'):
		response = libMediathek.getUrl(url)
		root = ET.fromstring(response)
		l = []
		for childNode in root.find('childNodes'):
			if childNode.attrib.get('name','') == 'mdr-core:broadcastDays':
				for childNode2 in childNode.find('childNodes'):
					d = {}
					for property in childNode2.find('properties'):
						if property.attrib.get('name','') == 'sophora:reference':
							document = property.find('document')
							d['url'] = document.find('customElements').find('metaxmlUrl').text
							for property2 in document.find('properties'):
								if property2.attrib.get('name','') == 'mdr-core:date':
									d['name'] = property2[0].text
									d['date'] = property2[0].text
					d['_type'] = 'dir'
					d['mode'] = 'libMdrBroadcast'
					l.append(d)
		return l

	def parseBroadcast(url):
		response = libMediathek.getUrl(url)
		root = ET.fromstring(response)
		l = []
		for childNode in root.find('childNodes'):
			d = {}
			for property in childNode.find('properties'):
				if property.attrib.get('name','') == 'sophora:reference':
					broadcast = property.find('document')
					if broadcast != None:
						for node in broadcast:
							if node.tag == 'videos':
								d['url'] = node[0][0][0][1].text#todo: makemrobust
							elif node.tag == 'properties':
								for node2 in node:#mdr-core:episodeText
									if node2.attrib.get('name','') == 'mdr-core:episodeText':
										d['_name'] = node2[0].text
									if node2.attrib.get('name','') == 'mdr-core:headline':
										d['_tvshowtitle'] = node2[0].text
										if not '_name' in d:
											d['_name'] = node2[0].text
									if node2.attrib.get('name','') == 'mdr-core:fsk':
										d['_mpaa'] = node2[0].text
									if node2.attrib.get('name','') == 'mdr-core:language':
										d['_lang'] = node2[0].text
									if node2.attrib.get('name','') == 'mdr-core:episodeNumber':
										d['_episode'] = node2[0].text
									if node2.attrib.get('name','') == 'mdr-core:duration':
										s = node2[0].text.split(':')
										d['_duration'] = str(int(s[0]) * 3600 + int(s[1]) * 60 + int(s[2]))
							elif node.tag == 'childNodes':
								for node2 in node:
									if node2.attrib.get('name','') == 'mdr-core:teaserImage':
										d['_thumb'] = _getThumb(node2)
									elif node2.attrib.get('name','') == 'mdr-core:copyText':
										try:
											for node3 in node2:
												if node3.tag == 'childNodes':
													for property2 in node3[0][0]:
														if property2.attrib.get('name','') == 'sophora-extension:text':
															if property2[0].text != None:
																d['_plot'] = property2[0].text.replace('<br/>','\n')
										except: pass
			d['_type'] = 'video'
			d['mode'] = 'libMdrPlay'
			if "name" in d:
				l.append(d)
		return l
		
	"""
	def parseMdrPlus(self,url):
		response = requests.get(url).text
		root = ET.fromstring(response)
		for property1 in root.find('childNodes').find('childNode').find('childNodes').find('childNode').find('childNodes').find('childNode').find('properties'):
			if property1.attrib.get('name','') == 'sophora:reference':
				#for document in property1.find('property').find('document').find('customElements').find('queryResult'):
				for document in property1.find('document').find('customElements').find('queryResult'):
					
					d = {'type':'video', 'params':{'mode':'libMdrPlay'}, 'metadata':{'art':{}}}
					if document.find('customElements').find('duration') is not None:
						d['metadata']['duration'] = self._durationToS(document.find('customElements').find('duration').text)
					d['params']['url'] = document.find('customElements').find('metaxmlUrl').text
					for property2 in document.find('properties'):
						if property2.attrib.get('name','') == 'mdr-core:headline':
							d['metadata']['name'] = property2[0].text
						if property2.attrib.get('name','') == 'mdr-core:teaserText':
							if property2[0].text is not None:
								d['metadata']['plot'] = property2[0].text
					for childNode in document.find('childNodes'):
						if childNode.attrib.get('name','') == 'mdr-core:teaserImage':
							d['metadata']['art']['thumb'] = self._getThumb(childNode)
					self.result['items'].append(d)
		return self.result

	def parsePlus(self,url):
		response = requests.get(url).text
		root = ET.fromstring(response)
		for document in root.find('customElements').find('queryResult'):
			d = {'type':'video', 'params':{'mode':'libMdrPlay'}, 'metadata':{'art':{}}}
			d['params']['url'] = document.find('customElements').find('metaxmlUrl').text
			if document.find('customElements').find('duration') is not None:
				d['metadata']['duration'] = self._durationToS(document.find('customElements').find('duration').text)
			for property2 in document.find('properties'):
				if property2.attrib.get('name','') == 'mdr-core:headline':
					d['metadata']['name'] = property2[0].text
					if d['metadata']['name'].startswith('Livestream: '): d['metadata']['name'] = d['metadata']['name'][12:]
					elif d['metadata']['name'].startswith('Livestream - '): d['metadata']['name'] = d['metadata']['name'][13:]
				if property2.attrib.get('name','') == 'mdr-core:teaserText':
					if property2[0].text is not None:
						d['metadata']['plot'] = property2[0].text
			for childNode in document.find('childNodes'):
				if childNode.attrib.get('name','') == 'mdr-core:teaserImage':
					d['metadata']['art']['thumb'] = self._getThumb(childNode)
			self.result['items'].append(d)
		return self.result

	def parseVideo(self,url):
		d = {'media':[]}
		if url.endswith('m3u8'):
			d['media'] = [{'url':video, 'type':'video', 'stream':'HLS'}]
			return d #m3u8 already supplied!?!?'
		if 'eventlivestreamzweiww-1378' in url:
			d['media'] = [{'url':'https://mdrevent2hls-lh.akamaihd.net/i/livetvmdrevent2_ww@513991/master.m3u8', 'type':'video', 'stream':'HLS'}]
			return d
		response = requests.get(url).text
		video = re.compile('<adaptiveHttpStreamingRedirectorUrl>(.+?)</adaptiveHttpStreamingRedirectorUrl>', re.DOTALL).findall(response)[0]
		d['media'] = [{'url':video, 'type':'video', 'stream':'HLS'}]
		if '<videoSubtitleUrl>' in response:
			sub = re.compile('<videoSubtitleUrl>(.+?)</videoSubtitleUrl>', re.DOTALL).findall(response)[0]
			d['subtitle'] = [{'url':sub, 'type': 'ttml', 'lang':'de'}]
		return d

	def _getThumb(self,teaserImage):
		for property in teaserImage.find('properties'):
			if property.attrib.get('name','') == 'sophora:reference':
				return property.find('document').find('customElements').find('teaserimageResponsive').find('url').text.replace('**imageVariant**','variantBig16x9').replace('**width**','960')
				try:
				#	return property.find('document').find('customElements').find('htmlUrl').text.replace('.html','-resimage_v-variantBig16x9_w-960.png?version=4333')
					return property.find('document').find('customElements').find('teaserimageResponsive').find('url').text.replace('**imageVariant**','variantBig16x9').replace('**width**','960')
				except: 
					return ''
	def _durationToS(self,d):
		s = d.split(':')
		if len(s) == 2:
			return str(int(s[0]) * 60 + int(s[1]))
		else:
			return '0'