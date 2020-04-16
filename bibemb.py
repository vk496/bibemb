import os, sys
import urllib.request
from pybtex.database import parse_file


ifile=sys.argv[1]
res_dir="bib_external_resources"
cur_dir=os.path.dirname(os.path.abspath(__file__))
BIBDIR=cur_dir + os.sep + res_dir


bibfile = cur_dir + os.sep + ifile

if not os.path.exists(bibfile):
    raise FileNotFoundError(f"Can't find {bibfile}")


if os.WEXITSTATUS(os.system(f"monolith -V")):
    raise Exception(f"Missing monolith software. Please install it from https://github.com/Y2Z/monolith")

if not os.path.exists(BIBDIR):
    os.makedirs(BIBDIR)


bib_data = parse_file(bibfile)

for key in bib_data.entries:

    if 'url' not in bib_data.entries[key].fields:
        print(f"Bib entry {key} don't have a url. Skipping...")
        continue
    else:
        url = bib_data.entries[key].fields['url']

    status_file = BIBDIR + os.sep + '.' + key

    if os.path.isfile(status_file):
        with open(status_file, 'r') as the_file:
            if url == the_file.read():
                print(f"{key} didn't change. Skipping")
                continue

    # print(f"{key}: {url}")
    # Request to file
    try:
        r = urllib.request.urlopen(url)
    except:
        print(f"Error requesting {url}. Skipping")
        continue


    # Get file type
    content_type = r.headers.get('content-type')
    if 'application/pdf' in content_type:
        ext = "pdf"
    else:
        ext = "html"


    output_file = f"{BIBDIR}{os.sep}{key}.{ext}"


    if ext == "pdf":
        print(f"Downloading raw {url} as {output_file}")
        data = r.read()
        with open(output_file, "wb") as file:
            file.write(data)
        r.close()
    else:
        print(f"GENERATING html with {url} as {output_file}")
        
        if os.WEXITSTATUS(os.system(f"monolith -k -I {url} -o {output_file}")):
            print(f"Error processing {key}. Cleaning")
            os.remove(output_file)
            continue

        size = os.stat(output_file).st_size

        #If file is more than 5MB, probably there are useless fonts. Save without css
        if size > 5000000:
            if os.WEXITSTATUS(os.system(f"monolith -k -I -c {url} -o {output_file}")):
                print(f"Error processing {key}. Cleaning")
                os.remove(output_file)
                continue
    
    with open(status_file, 'w') as the_file:
        the_file.write(url)

    