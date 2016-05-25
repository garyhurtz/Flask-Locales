# -*- coding: UTF-8 -*- #

import codecs
import yaml
import os
import errno

from flask import json


def yaml_loader(cls, path):
    """
    Load localized context from a yaml file

    :param cls: placeholder for class
    :param path: the path to load from
    :return: the context
    """

    with codecs.open(path, u'r', u'utf-8') as infile:
        context = yaml.load(infile)

    return context


def json_loader(cls, path):
    """
    Load localized context from a json file

    :param cls: placeholder for class
    :param path: the path to load from
    :return: the context
    """

    with codecs.open(path, u'r', u'utf-8') as infile:
        context = json.load(infile)

    return context


def json_caching_yaml_loader(cls, yaml_path):
    """
    Load localized context from a yaml, and cache to json

    Continue to json as long as it is current, update if/when yaml is updated

    Json is cached in .cc/, to minimize directory noise

    :param cls: placeholder for class
    :param yaml_path: the path to the context file.
    :return: the context
    """

    path_list = yaml_path.replace(u'.yaml', u'.json').rsplit(os.sep, 1)
    path_list.insert(len(path_list) - 1, u'.cc')
    json_path = os.path.join(*path_list)

    # if json does not exist, or
    # if yaml file has been modified since json was written
    # then update the json
    if not os.path.exists(json_path) or os.path.getmtime(yaml_path) > os.path.getmtime(json_path):

        # load yaml
        context = yaml_loader(cls, yaml_path)

        # create cache directory, if needed
        json_dir = os.path.dirname(json_path)

        if not os.path.exists(json_dir):
            try:
                os.makedirs(json_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        # write json
        with codecs.open(json_path, u'w', u'utf-8') as outfile:
            json.dump(context, outfile)

        # return the context
        return context

    return json_loader(cls, json_path)
