from functools import update_wrapper

import click


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