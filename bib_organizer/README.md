# bib_organizer

* [Main readme](README.md)

Code to facilitate on the organization of .bib files and check for repeated references.

This code can:

 * Flatten the .bib file
 * Sort the flattened .bib file by author name to check for duplicates
 * Unflatten the flatenned .bib file

## How to use

The main idea is to create a a flattened version of your .bib file (`file.flat.bib`) and a file with the references sorted by author name to check for duplicates (`file.sort.bib`).
The `file.flat.bib` will be your main file,
where you make the editions that will be later converted back to your original `file.bib`.

### Basic Use

1.Run the basic command that creates a file `file.flat.bib` containing a flattened version of your .bib file:


    python flat_bib.py file.bib


Only the lines starting with `@`, `%-` or `% *` will generate different lines in `file.flat.bib`,
so you should make your comments with these prefixes.
Alternatively,
you can just add any other prefixes by inserting them into the array `break_line` at line 4 of `flat_bib.py`. 

2.Run the command to create a file `file.sort.bib` with the bib sorted by author name.
(This command will also create a `file.flat.bib` file if it does not exist.)

    python flat_bib.py file.bib -t s

By default, the sorted file only displays the reference name and title field.
If you want to change the field displayed to a certain `FIELD_NAME`, 
add the key `-f FIELD_NAME`.

3.Check for repeated references in `file.sort.bib` and fix it in `file.flat.bib`.
You can also use this moment to edit `file.flat.bib` and organize the order of your references.

4.Run the command to convert `file.flat.bib` back to the original .bib file.

    python flat_bib.py file.bib -t u

**Now organizing the .bib references in your life will be easier :)**

**NOTES:** 

* If you use `vim` as your file editor,
using the command `:set nowrap` when viewing `file.flat.bib` 
can be very helpful to stop `vim` from breaking lines.

* The code does not have to be run inside the main directory (`bib_organizer/`),
you can just add the path of the main directory and run `python path_to_bib_organizer/flat_bib.py`

* The code does not have to be run inside the directory of the .bib file,
you can just add the path of the .bib file and run `python flat_bib.py path_to_bibfile/file.bib`

* You can combine both items above: `python path_to_bib_organizer/flat_bib.py path_to_bibfile/file.bib`

* If you give executable permition to the `flat_bib.py` (`chmod u+x flat_bib.py`),
you do not have to run `python` before `flat_bib.py`.

### Adding to your paths

Another option is to add the code path to your paths by going inside the main directory (`bib_organizer/`)
and running:

    . SOURCE

or

    source SOURCE

Then you can simply call `flat_bib` from anywhere instead of running `python path_to_bib_organizer/flat_bib.py`.
