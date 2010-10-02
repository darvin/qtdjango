#!/usr/bin/env python

# Classes for generic microblog exceptions

class MicroBlogMsgLimitExceeded(Exception):
    def __str__(self):
        return "Message limit size was exceeded"
