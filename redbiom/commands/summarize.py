import click

from . import cli


@cli.group()
def summarize():
    """Summarize things."""
    pass


@summarize.command(name='contexts')
def summarize_caches():
    """List names of available caches"""
    import redbiom.summarize
    contexts = redbiom.summarize.contexts()

    if contexts:
        click.echo("Name\tDescription\n")
        for name, desc in sorted(contexts.items()):
            click.echo("%s\t%s" % (name, desc))
    else:
        click.echo("No available contexts")


@summarize.command(name='metadata-category')
@click.option('--category', required=True,
              help="The metadata category (i.e., column) to summarize")
@click.option('--counter', required=False, is_flag=True, default=False,
              help="If true, obtain value counts")
@click.option('--descending', is_flag=True, required=False, default=False,
              help="If true, sort in descending order")
@click.option('--dump', required=False, is_flag=True, default=False,
              help="If true, print the sample information.")
@click.option('--sort-index', is_flag=True, required=False, default=False,
              help=("If true, sort on the index instead of the values. This "
                    "option is only relevant when --counter is specified."))
def summarize_metadata_category(category, counter, descending, dump,
                                sort_index):
    """Summarize the values within a metadata category"""
    if not counter and not dump:
        click.echo("Please specify either --counter or --dump",
                   err=True)
        import sys
        sys.exit(1)

    import redbiom.fetch
    md = redbiom.fetch.category_sample_values(category)

    if counter:
        click.echo("Category value\tcount")
        counts = md.value_counts(ascending=not descending)
        if sort_index:
            counts = counts.sort_index(ascending=not descending)

        for idx, val in zip(counts.index, counts):
            click.echo("%s\t%s" % (idx, val))
    else:
        click.echo("#SampleID\t%s" % category)
        for idx, val in zip(md.index, md):
            click.echo("%s\t%s" % (idx, val))


@summarize.command(name='metadata')
@click.option('--descending', is_flag=True, required=False, default=False,
              help="If true, sort in descending order")
def summarize_metadata(descending):
    """Get the known metadata categories and associated sample counts"""
    import redbiom.fetch
    md = redbiom.fetch.sample_counts_per_category()
    md = md.sort_values(ascending=not descending)

    for idx, val in zip(md.index, md):
        click.echo("%s\t%s" % (idx, val))


@summarize.command(name='observations')
@click.option('--from', 'from_', type=click.File('r'), required=False,
              default=None)
@click.option('--category', type=str, required=True)
@click.option('--exact', is_flag=True, default=False,
              help="All found samples must contain all specified observations")
@click.option('--context', required=True, type=str)
@click.argument('observations', nargs=-1)
def summarize_observations(from_, category, exact, context,
                           observations):
    """Summarize observations over a metadata category."""
    import redbiom.util
    iterable = redbiom.util.from_or_nargs(from_, observations)

    import redbiom.summarize
    md = redbiom.summarize.category_from_observations(context, category,
                                                      iterable, exact)

    cat_stats = md.value_counts()
    for val, count in zip(cat_stats.index, cat_stats.values):
        click.echo("%s\t%s" % (val, count))
    click.echo("\n%s\t%s" % ("Total samples", sum(cat_stats.values)))


@summarize.command(name='samples')
@click.option('--from', 'from_', type=click.File('r'), required=False,
              default=None)
@click.option('--category', type=str, required=True)
@click.argument('samples', nargs=-1)
def summarize_samples(from_, category, samples):
    """Summarize samples over a metadata category."""
    import redbiom.util
    iterable = redbiom.util.from_or_nargs(from_, samples)

    import redbiom.summarize
    md = redbiom.summarize.category_from_samples(category, iterable)

    cat_stats = md.value_counts()
    for val, count in zip(cat_stats.index, cat_stats.values):
        click.echo("%s\t%s" % (val, count))
    click.echo("\n%s\t%s" % ("Total samples", sum(cat_stats.values)))
