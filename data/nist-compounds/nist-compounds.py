#!/usr/bin/env python3


import urllib.request
from io import StringIO
import lxml.etree as ET
import sys
import re

nist_url = "http://physics.nist.gov/cgi-bin/Star/compos.pl?matno="

with open("../../src/xraylib-nist-compounds-internal.h", "w") as output_int, open("../../include/xraylib-nist-compounds.h", "w") as output_header:

    header_begin = '''/*
Copyright (c) 2013-1018, Tom Schoonjans
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * The names of the contributors may not be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Tom Schoonjans ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Tom Schoonjans BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 * This file was automatically generated by nist-compounds.py
 * Modify at your own risk...
 */


#ifndef XRAYLIB_NIST_COMPOUNDS_H
#define XRAYLIB_NIST_COMPOUNDS_H

#include "xraylib-error.h"

struct compoundDataNIST {
	char *name;
        int nElements;
        int *Elements;
        double *massFractions;
        double density;
};

/*
 *
 * Returns a pointer to a newly allocated struct containing
 * the requested compound on success, or NULL when the compound
 * was not found in the list. The compound is requested by providing
 * its name as argument to the function. For a list of available names,
 * use GetCompoundDataNISTList.
 *
 * The returned struct should be freed after usage with FreeCompoundDataNIST.
 *
 */
XRL_EXTERN
struct compoundDataNIST* GetCompoundDataNISTByName(const char compoundString[], xrl_error **error);

/*
 *
 * Returns a pointer to a newly allocated struct containing
 * the requested compound on success, or NULL when the compound
 * was not found in the list. The compound is requested by providing
 * its index in the internal table to the function. Typically this would
 * be done using the NIST_COMPOUND_* macros in this file.
 *
 * The returned struct should be freed after usage with FreeCompoundDataNIST.
 *
 */
XRL_EXTERN
struct compoundDataNIST* GetCompoundDataNISTByIndex(int compoundIndex, xrl_error **error);

/*
 *
 * Returns a NULL-terminated array of strings of all the compounds in the
 * internal table. If nCompounds is not NULL, it shall receive the number 
 * of compounds.
 *
 * The returned array should be freed firstly by using xrlFree to deallocate
 * all individual strings, and subsequently by using xrlFree to deallocate the array
 *
 */
XRL_EXTERN
char **GetCompoundDataNISTList(int *nCompounds, xrl_error **error);

/*
 *
 * Deallocates a pointer to a compoundDataNIST struct completely.
 * It is recommended to set the pointer to NULL after calling this function.
 *
 */
XRL_EXTERN
void FreeCompoundDataNIST(struct compoundDataNIST *compoundData);

'''

    output_header.write(header_begin)

    header_begin2 = '''/*
Copyright (c) 2013-2018, Tom Schoonjans
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * The names of the contributors may not be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Tom Schoonjans ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Tom Schoonjans BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 * This file was automatically generated by nist-compounds.pl
 * Modify at your own risk...
 */

#include <xraylib-nist-compounds.h>

'''

    output_int.write(header_begin2)

    compoundData = []

    for compoundIndex, i in enumerate(range(99, 279)):
        url = '{}{:03}.html'.format(nist_url, i)
        print("URL: {}".format(url))

        try:
            response = urllib.request.urlopen(url)
            html = response.read().decode("utf-8")

            #fix html file
            html = re.sub(r"(<form action=\"\/cgi-bin\/Star\/compos.pl\" method=GET>)\n(<center>)", r"\2\n\1", html, flags=re.M)
            html = re.sub("<a\n", "\n", html)
            html = re.sub(r"<script.+<\/script>", "", html)
            parser = ET.HTMLParser()
            tree = ET.parse(StringIO(html), parser)

            searchstring = "//body/center/form/select/option[@value='{:03}']/text()".format(i)

            name = tree.xpath(searchstring)[0]
            density = tree.xpath("//body/center/table[1]/tr[1]/td[2]/text()")[0]

            nodes = tree.xpath("//body/center/table[2]/tr[@align='right']")

            Elements = []
            massFractions = []

            for node in nodes:
                Elements.append(node.xpath("td[1]/text()")[0])
                massFractions.append(node.xpath("td[2]/text()")[0])

            compoundDataSingle = dict(name=name, density=density, nElements=len(nodes), Elements=Elements, massFractions=massFractions)
            compoundData.append(compoundDataSingle)

            #macro
            macro = name.upper()
            macro = re.sub(', ', '_', macro)
            macro = re.sub(' ', '_', macro)
            macro = re.sub('-', '_', macro)
            macro = re.sub(r'\(', '', macro)
            macro = re.sub(r'\)', '', macro)
            macro = re.sub(',', '', macro)
            macro = re.sub('/', '', macro)

            output_header.write("#define NIST_COMPOUND_{} {}\n".format(macro, compoundIndex))
        except Exception as e:
            print(e)
            raise



    output_int.write("static const int nCompoundDataNISTList = {};\n".format(len(compoundData)))

    for i, cd in enumerate(compoundData):
        output_int.write("static int __CompoundDataNISTList_Elements_{}[] = {{{}}};\n".format(i, ", ".join(cd['Elements'])))
        output_int.write("static double __CompoundDataNISTList_massFractions_{}[] = {{{}}};\n".format(i, ", ".join(cd['massFractions'])))

    output_int.write("static const struct compoundDataNIST compoundDataNISTList[] = {\n")

    #output_int.write("{{\"{}\" ,{}, __CompoundDataNISTList_Elements_{}, __CompoundDataNISTList_massFractions_{}, {}}}".format(cd['name'], cd['nElements'], i, i, cd['density']))
    ls = ["{{\"{}\" ,{}, __CompoundDataNISTList_Elements_{}, __CompoundDataNISTList_massFractions_{}, {:f}}}".format(cd['name'], cd['nElements'], i, i, float(cd['density'])) for i, cd in enumerate(compoundData)]
    output_int.write(",\n".join(ls) + "\n")

    output_int.write("};\n")

    output_header.write("\n#endif\n")

