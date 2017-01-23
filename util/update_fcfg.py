import glob
import os, sys, inspect
import re

file_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(file_folder, '..'))

from datastore.aws_datastore import AWSDataStore

def updatePartnerFile(partner):
    print "PARTNER: " + partner.upper()

    ds = AWSDataStore(partner, 'startup8-server')
    productInfo = ds.getAllProductAttibutes()
    locationInfo = ds.getAllLocationAttibutes()

    # find all the files in the config dir
    currentLocation = os.path.dirname(os.path.realpath(__file__))
    cfgFiles = glob.glob(os.path.join(currentLocation, '..', 'common', '*.fcfg'))

    # loop though each file replace data
    for fcfgFile in cfgFiles:
        print '---------------------------'
        content = ''
        words = []
        with open(fcfgFile) as f:
            content += f.read()
        print '->COLOR'

        # print content
        oldStr = re.findall('(# COLOR BEGIN)(.*?)(# COLOR END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['colors'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "JJ[SEM = 'color=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2], oldStr[0][0] + newStr + oldStr[0][2])

        print '->STYLE'
        oldStr = re.findall('(# STYLE BEGIN)(.*?)(# STYLE END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['styles'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "JJ[SEM = 'style=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2], oldStr[0][0] + newStr + oldStr[0][2])

        print '->OCCASION'
        oldStr = re.findall('(# OCCASION BEGIN)(.*?)(# OCCASION END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['occasion'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'occasion=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2], oldStr[0][0] + newStr + oldStr[0][2])

        print '->PRODUCT\n'
        oldStr = re.findall('(# PRODUCT BEGIN)(.*?)(# PRODUCT END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['products'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'goods=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])

        oldStr = re.findall('(# BRAND BEGIN)(.*?)(# BRAND END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['brands'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'brand=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])

        oldStr = re.findall('(# SIZE STRING BEGIN)(.*?)(# SIZE STRING END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['sizes'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'size=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])

        # DESCRIPTION BEGIN
        oldStr = re.findall('(# DESCRIPTION BEGIN)(.*?)(# DESCRIPTION END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(productInfo['description'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'descriptor=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])

        # LOCATION BEGIN
        oldStr = re.findall('(# LOCATION BEGIN)(.*?)(# LOCATION END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(locationInfo['locations'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'location=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

                    if partner in tmp.lower():
                        tmp = tmp.replace(partner, '').strip()
                        if tmp and  len(tmp) >= 3 and not tmp in ds.globalBlackList:
                            newStr += "N[SEM = 'location=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                            words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])

        # LOCATION NAME BEGIN
        oldStr = re.findall('(# LOCATION NAME BEGIN)(.*?)(# LOCATION NAME END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(locationInfo['names'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'location=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

                # remove partner
                if partner in tmp.lower():
                    tmp = tmp.replace(partner, '').strip()
                    if not tmp in words:
                        if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                            newStr += "N[SEM = 'location=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                            words.append(tmp)

                # remove common suffixes
                tmp = tmp.lower()
                tmp = tmp.replace(partner, '').strip()
                if tmp.endswith('mall'):
                    tmp = tmp.replace('mall', '').strip()
                if tmp.endswith('square'):
                    tmp = tmp.replace('square', '').strip()
                if tmp.endswith('shopping center'):
                    tmp = tmp.replace('shopping center', '').strip()
                if tmp.endswith('plaza'):
                    tmp = tmp.replace('plaza', '').strip()
                if tmp.endswith('town center'):
                    tmp = tmp.replace('town center', '').strip()
                if tmp.endswith('towne centre'):
                    tmp = tmp.replace('towne centre', '').strip()
                if tmp.endswith('fashion center'):
                    tmp = tmp.replace('fashion center', '').strip()
                if tmp.endswith('pavilion'):
                    tmp = tmp.replace('pavilion', '').strip()
                if tmp.endswith('galleria'):
                    tmp = tmp.replace('galleria', '').strip()
                if tmp.endswith('center'):
                    tmp = tmp.replace('center', '').strip()
                if tmp.endswith('centre'):
                    tmp = tmp.replace('centre', '').strip()

                tmp = re.sub(r' at .*$', '', tmp).strip()

                if not tmp in words:
                    if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                        newStr += "N[SEM = 'location=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                        words.append(tmp)


            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])

        # ZIPCODE BEGIN
        oldStr = re.findall('(# ZIPCODE BEGIN)(.*?)(# ZIPCODE END)', content, re.DOTALL)
        if oldStr:
            newStr = '\n'

            # sort by len
            strList = list(locationInfo['zipcodes'])
            strList.sort(key=lambda s: len(s), reverse=True)

            for tmp in strList:
                if tmp and len(tmp) >= 3 and not tmp in ds.globalBlackList:
                    newStr += "N[SEM = 'zipcode=\"" + tmp + "\"'] -> '" + tmp.replace(' ', '_') + "'" + '\n'
                    words.append(tmp)

            content = content.replace(oldStr[0][0] + oldStr[0][1] + oldStr[0][2],
                                      oldStr[0][0] + newStr + oldStr[0][2])


        partnerPath = os.path.join(os.path.dirname(fcfgFile), '..', 'partner', partner)

        if not os.path.isdir(partnerPath):
            os.mkdir(partnerPath)

        with open(os.path.join(partnerPath, 'words.txt'), 'w') as foutwords:
            foutwords.write('\n'.join(words))

        with open(os.path.join(partnerPath, os.path.basename(fcfgFile)), 'w') as fout:
            fout.write(content)


def main(args=None):
    print 'Working ...\n'

    updatePartnerFile('nordstrom')
    updatePartnerFile('bestbuy');
    updatePartnerFile('target');

    print 'Done ...'

if __name__ == "__main__":
    main()
