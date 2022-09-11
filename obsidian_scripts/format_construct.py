import pandas as pd
import click

@click.command()
@click.argument('csv')
def main(csv):
    df = pd.read_csv(csv)
    f = open("test", "w")
    for i, row in df.iterrows():
        f.write(f"## {row['name']}\n")
        f.write("<table border='1' width='100%'>\n")
        f.write("  <tr>\n")
        f.write("    <th>key</th>\n")
        f.write("    <th>value</th>\n")
        f.write("  </tr>\n")
        vals = [
            ['name', row['name']],
            ['sequence', row['sequence']],
            ['structure', row['structure']]
        ]
        for k, v in vals:
            f.write(f"  <tr>\n")
            f.write(f"  <td>{k}</td>\n")
            f.write(f"  <td>{v}</td>\n")
            f.write(f"  </tr>\n")
        f.write("</table>\n\n")
    f.close()

if __name__ == '__main__':
    main()