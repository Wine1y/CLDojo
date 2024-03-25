from functools import update_wrapper

import click

from utils.config import Config
from classes.language import any_language_by_name


def pass_client(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.ensure_object(dict)
        return ctx.invoke(f, ctx.obj.get("client"), *args, **kwargs)
    return update_wrapper(new_func, f)

def pass_keeper(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.ensure_object(dict)
        return ctx.invoke(f, ctx.obj.get("keeper"), *args, **kwargs)
    return update_wrapper(new_func, f)

def pass_config(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.ensure_object(dict)
        return ctx.invoke(f, ctx.obj.get("config"), *args, **kwargs)
    return update_wrapper(new_func, f)

def pass_styler(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.ensure_object(dict)
        return ctx.invoke(f, ctx.obj.get("styler"), *args, **kwargs)
    return update_wrapper(new_func, f)

def pass_default_languages(provider:str):
    def inner(f):
        @pass_config
        @click.pass_context
        def new_func(ctx, config: Config, *args, **kwargs):
            default_languages = {
                any_language_by_name(config.get("providers", provider, "default_language")),
                any_language_by_name(config.get("providers", provider, "default_shell_language")),
                any_language_by_name(config.get("providers", provider, "default_sql_dialect"))
            }
            return ctx.invoke(f, default_languages, *args, **kwargs)
        return update_wrapper(new_func, f)
    return inner