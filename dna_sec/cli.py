import click
import json
from .parser import load_dna_sequence
from .scanner import scan_dna_for_malware


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Fichier JSON de sortie")
def scan(file_path, output):
    """Analyse un fichier d'ADN pour détecter du malware."""
    try:
        dna_seq = load_dna_sequence(file_path)
        report = scan_dna_for_malware(dna_seq)

        if output:
            with open(output, "w") as f:
                json.dump(report, f, indent=2)
            click.echo(f"Rapport sauvegardé dans {output}")
        else:
            click.echo(json.dumps(report, indent=2))

    except Exception as e:
        click.echo(f"Erreur : {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    scan()
