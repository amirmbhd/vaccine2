#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 04:33:36 2023

@author: amirbhd
"""

"""Hack to add per-session state to Streamlit.
Usage
-----
>>> import SessionState
>>>
>>> state = SessionState.get(user_name='', favorite_color='black')
>>> state.user_name
''
>>> state.user_name = 'Mary'
>>> state.favorite_color
'black'
"""

class _SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def get(**kwargs):
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server

    session = ReportThread.get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session)

    if session_info is None:
        raise RuntimeError('Could not get your Streamlit Session object.')

    if not hasattr(session_info, 'session_state'):
        session_info.session_state = _SessionState(**kwargs)

    return session_info.session_state
