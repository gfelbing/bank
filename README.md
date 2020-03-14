# bank

Scripts to parse and analyse CSV exports of [DKB](https://www.dkb.de).

## Setup

Store the csv exports from DKB within the `csv` folder.

Create a file `group_defs.py` containing regular expressions for transactions, for better grouping, e.g.:

```python
groups={
        r'my favorite restaurant': "Restaurant",
        r'my 2nd fav restaurant': "Restaurant",
        r'.*': "Misc",
}
```

Run the script, passing the CSV files to anaylse, e.g.: `python group.py csv/*.csv`
