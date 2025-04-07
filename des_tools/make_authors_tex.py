#!/usr/bin/env python
# coding: utf-8

import numpy as np
from astropy.table import Table


def smart_split(line):
    if '"' not in line:
        return line.split(",")
    out = []
    _line = line.replace('\\""', ";")
    for l in _line.split('"'):
        if len(l) == 0:
            out.append(l)
        elif l[-1] == ",":
            out += l.split(",")[:-1]
        else:
            out.append(l)
    out = [o.replace(";", '\\"') for o in out]
    return out


def fmt_firstname(firstname):
    out = []
    for n in firstname.split(" "):
        if "." in n:
            out.append()
        else:
            out += n[0]


def prt_command(itemlist):
    return "\n    \\and\n".join([f"    {a}" for a in itemlist])


class ProcessData:
    @property
    def affiliations(self):
        return self.main_affiliation + self.other_affiliation

    @property
    def authors(self):
        return self.main_authors + self.other_authors

    def __init__(self, input_file):
        self.main_authors = []
        self.main_affiliation = []
        self.other_authors = []
        self.other_affiliation = []
        self.read_data(input_file)

    def _read_data(self, input_file):
        return [d.replace("\n", "") for d in open(input_file).readlines()]

    def _data_to_table(self, data):
        _data_fmt = []
        for d in data[:]:
            # print(d)
            _data_fmt.append(smart_split(d))
        return Table(np.array(_data_fmt[1:]), names=_data_fmt[0])

    def read_data(self, input_file):
        self.data = self._data_to_table(self._read_data(input_file))
        self.authors_set = sorted(set(self.data["Lastname"]))
        self._set_other_authors()
        self._set_other_affiliation()
        self._set_affiliation_dict()

    def show_sizes(self):
        print(
            len(set(self.data["Lastname"])),
            len(set([d["Firstname"] + d["Lastname"] for d in self.data])),
        )

    def _set_other_authors(self):
        self.other_authors = sorted(
            set([a for a in self.data["Lastname"] if a not in self.main_authors])
        )

    def set_main_authors(self, main_authors=None):
        if main_authors is None:
            main_authors = []
        self.main_authors = main_authors
        self._set_other_authors()
        self.emails = [
            self.data["Email"][self.data["Lastname"] == author][0]
            for author in self.authors
        ]

    def show_authors_list(self):
        print(self.authors_set)

    def show_main_affiliations(self):
        main_aff_inds = np.where(np.isin(self.data["Lastname"], self.main_authors))[0]
        for i in main_aff_inds:
            print(
                f"{i:4}",
                self.data["Affiliation"][i][:30],
                self.data["Lastname"][i][:10],
            )

    def _set_other_affiliation(self):
        self.other_affiliation = []
        for author in self.other_authors:
            for af in self.data["Affiliation"][self.data["Lastname"] == author]:
                if (
                    af not in self.main_affiliation
                    and af not in self.other_affiliation
                    and af != ""
                ):
                    self.other_affiliation.append(af)

    def _set_affiliation_dict(self):
        self.affiliation_dict = {
            af: f"{i+1:d}" for i, af in enumerate(self.affiliations)
        }

    def set_main_affiliations(self, main_aff_inds):
        self.main_aff_inds = main_aff_inds
        print("Main affiliations set to:")
        for i in main_aff_inds:
            print(self.data["Affiliation"][i])

        self.main_affiliation = [
            self.data["Affiliation"][i] for i in self.main_aff_inds
        ]
        self._set_other_affiliation()
        self._set_affiliation_dict()

    def _get_formated_author_list(self, typ=1):
        _fmt_ref = {
            1: lambda ref: f"\\inst{{{ref}}}",
            2: lambda ref: f"$^{{{ref}}}$",
        }[typ]

        fmt_author_list = []
        for author in self.authors:
            aff = [
                self.affiliation_dict[dat]
                for dat in self.data["Affiliation"][self.data["Lastname"] == author]
                if dat != ""
            ]
            firstname = "".join(
                [
                    f"{n[0]}."
                    for n in self.data["Firstname"][self.data["Lastname"] == author][
                        0
                    ].split(" ")
                    if n[0].upper() == n[0]
                ]
            )
            fmt_author_list.append(
                f"{firstname} {author} {_fmt_ref(','.join(sorted(aff)))}"
            )
        return fmt_author_list

    def write_tex(self, typ=1, filename="authors.tex"):
        _fmt_author_list = self._get_formated_author_list(typ)
        out = f"\\author{{\n{prt_command(_fmt_author_list)}\n}}"
        if typ == 1:
            out += f"\n\\institute{{\n{prt_command(self.affiliations)}\n}}"

        elif typ == 2:
            affiliations_enum = "\n \\\\".join(
                [f"{i+1:3}. {aff}" for i, aff in enumerate(self.affiliations)]
            )
            out += (
                "\n\\institute{(Affiliations can be found after the references)}"
                f"\n\\newcommand{{\\institutes}}{{\n{affiliations_enum}\n}}"
            )

        f = open(filename, "w")
        print(out, file=f)
        f.close()

    def write_emails(self, filename="emails.txt"):
        f = open("emails.txt", "w")
        for e in self.emails:
            print(e, file=f)
        f.close()


class ProcessDataIter:
    def __init__(self):
        self.input_file = None
        self.outfile = None
        self.outfmt = None

    def read_data(self):
        print("Starting data processing")
        self.pd = ProcessData(self.input_file)

    def _pass(self):
        pass

    def run_actions(self, actions, message):
        action = input(message)
        while action not in actions:
            print("Action not valid!")
            action = input(message)
        return actions[action]()

    def confirm(self, action_func, value):
        _actions = {
            "y": lambda: value,
            "n": lambda: action_func(),
        }
        return self.run_actions(_actions, message=" * Confirm [y/n]: ")

    def get_input(self, message, func_valid_fmt=None):
        if func_valid_fmt is None:
            func_valid_fmt = self._valid_fmt_any

        _valid = False
        while not _valid:
            _input = input(message)
            _valid, _value = func_valid_fmt(_input)
            if not _valid:
                print(f'input:"{_input}" not valid')
        print(" * value set to:", _value)
        return self.confirm(lambda: self.get_input(func_valid_fmt, message), _value)

    # validation functions

    def _valid_fmt_any(self, value):
        return True, value

    def _valid_fmt_main_authors(self, value):
        if value == "":
            return True, []
        authors = value.replace(" ", "").split(",")
        bad_authors = list(
            filter(lambda _aut: _aut not in self.pd.authors_set, authors)
        )
        if len(bad_authors) > 0:
            print(f"     bad authors:", ", ".join(bad_authors))
            return False, None
        return True, authors

    def _valid_fmt_main_affiliations(self, value):
        if value == "":
            return True, []
        main_aff_inds = value.replace(" ", "").split(",")
        bad_inds = []
        for i in main_aff_inds:
            try:
                int(i)
            except:
                bad_inds.append(i)
        if len(bad_inds) > 0:
            print(f"     bad indexes:", ", ".join(bad_inds))
            return False, None
        return True, list(map(int, main_aff_inds))

    def _valid_fmt_output_file(self, value):
        if value == "":
            return True, "temp.tex"
        elif value[-4:] == ".tex":
            return True, value
        return False, None

    def _valid_fmt_output_type(self, value):
        if value in {"1", "2"}:
            return True, int(value)
        print("    Value must be 1 or 2!")
        return False, None

    # internal setting functions

    def _set_main_authors(self):
        self.pd.set_main_authors(
            self.get_input(
                "Main authors (lastname separated by comma): ",
                self._valid_fmt_main_authors,
            )
        )

    def _set_main_affiliations(self):
        self.pd.set_main_affiliations(
            self.get_input(
                "Main affiliation indexes (separated by comma): ",
                self._valid_fmt_main_affiliations,
            )
        )

    # main functions

    def set_input_file(self):
        self.input_file = self.get_input("Input file (.csv format): ")

    def set_main_authors(self):
        print("Setting main authors:")
        message = (
            " * Action [(s) Skip/(p) Print all authors/(w) Write main author list]: "
        )
        _actions = {
            "s": self._pass,
            "p": lambda: (self.pd.show_authors_list(), self._set_main_authors()),
            "w": self._set_main_authors,
        }
        self.run_actions(_actions, message=message)

    def set_main_affiliations(self):
        if not self.pd.main_authors:
            return
        print("Setting main affitiations: ")
        message = " * Action [(s) Skip/(p) Print all main affiliations/(w) Write main affilitaion indexes]: "
        _actions = {
            "s": self._pass,
            "p": lambda: (
                self.pd.show_main_affiliations(),
                self._set_main_affiliations(),
            ),
            "w": self._set_main_affiliations,
        }
        self.run_actions(_actions, message=message)

    def set_output_file(self):
        self.output_file = self.get_input(
            "Output file (defalt=temp.tex): ", self._valid_fmt_output_file
        )

    def set_output_type(self):
        self.output_type = self.get_input(
            "Output type [1/2]: ", self._valid_fmt_output_type
        )

    def write_tex(self):
        self.pd.write_tex(typ=self.output_type, filename=self.output_file)

    def write_emails(self):
        raise NotImplementedError()

    def run(self):
        self.set_input_file()
        self.read_data()
        self.set_main_authors()
        self.set_main_affiliations()
        self.set_output_type()
        self.set_output_file()
        print(f"Writting output to {self.output_file}")
        self.write_tex()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="Use config file.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        default=False,
        action="store_true",
        help="Run in interactive mode.",
    )
    args = parser.parse_args()

    if args.interactive:
        pdi = ProcessDataIter()
        pdi.run()
    else:
        pd = ProcessData(input_file)
        self.set_main_authors(main_authors)
        self.set_main_affiliations(main_aff_inds)
        self.write_tex(typ, filename=output)
