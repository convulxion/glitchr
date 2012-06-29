#!/usr/bin/env python
# -- coding: utf-8 --

# This is an interface to the specific bits of the tumblr
# API I'm interested in

import ConfigParser
import argparse

import os
import sys

from random import choice
from string import Template

from tumblpy import Tumblpy
from photo import Photo
from jpegglitcher import JpegGlitcher

def parseArgs():
    parser = argparse.ArgumentParser(description='Retrieve Photo Posts')
    parser.add_argument('config', help='The config file')
    args = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args.config)

    return config

def parseBlogPhotos(blog):
    allPhotos = []

    blogName = blog['blog']['title']
    blogUrl  = blog['blog']['url']

    for post in blog['posts']:

        postUrl  = post['post_url']
        postDate = post['date']

        for photo in post['photos']:

            imgUrl    = photo['original_size']['url']
            name, ext = os.path.splitext(imgUrl)

            # We only want jpeg images, because that's all I can glitch
            if ext == '.jpg' or ext == '.jpeg':
                data = {}
                data['blogName'] = blogName
                data['postUrl']  = postUrl
                data['blogUrl']  = blogUrl
                data['imgUrl']   = imgUrl
                data['postDate'] = postDate
                allPhotos.append(data)

    return allPhotos


# Go through parsing the response for each blog
def getFollowerPhotos(blog, tumblr):

    blogUrl = blog['url']
    params = {}
    params['tag'] = 'landscape'
    response = tumblr.api_request('posts',
                                  blogUrl,
                                  extra_endpoints=['photo'],
                                  params=params)

    photos = parseBlogPhotos(response)

    return photos

def getRandomPhoto(photos):
    photo = choice(photos)
    data = {}
    data['blogName']  = photo['blogName']
    data['postUrl']   = photo['postUrl']
    data['blogUrl']   = photo['blogUrl']
    data['postDate']  = photo['postDate']
    data['imgUrl']    = photo['imgUrl']
    data['imageData'] = Photo(photo['imgUrl'])
    return data

def createCaption(data):
    templt  = '<a href="$imgUrl">Original</a>'
    templt += ' image courtesy of '
    templt += '<a href="${blogUrl}">${blogName}</a>'
    templt += '\n'
    templt += '<a href="$postUrl">First posted</a>'
    templt += ' on ${postDate}'
    c = Template(templt)

    return c.substitute(data)


def main():

    config = parseArgs()
    consumerKey    = config.get('consumer', 'key')
    consumerSecret = config.get('consumer', 'secret')
    oauthToken     = config.get('oauth', 'key')
    oauthSecret    = config.get('oauth', 'secret')

    tumblr = Tumblpy(consumerKey, consumerSecret, oauthToken, oauthSecret)

    data = tumblr.api_request('user/following')

    followers = data['blogs']

    photos = []
    for blog in followers:
        blogPhotos =  getFollowerPhotos(blog, tumblr)
        if blogPhotos:
            photos += blogPhotos

    print('%s photos found to choose from' % len(photos))

    randImage = getRandomPhoto(photos)

    randImage['imageData'].retrieve()
    imgData = randImage['imageData'].getData()

    caption = createCaption(randImage)
    print(caption)

    parser = JpegGlitcher(imgData)
    parser.parse_data()
    parser.find_parts()
    parser.quantize_glitch()
    glitched = parser.output_file('output.jpg')
    glitched.name = 'file.jpeg'

    params = {}
    params['type'] = 'photo'
    params['caption'] = caption
    params['tags'] = 'glitch, generative, random'

    #response = tumblr.post('post', 'http://rumblesan.tumblr.com', params=params, files=glitched)
    #print('post id is %s' % response['id'])




if __name__ == '__main__':
    main()

