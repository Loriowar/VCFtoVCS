import re
import traceback

# Create single files with Vcalendar record, based on Vcard record
# Work with birthday. Get birth date from Vcard and create new record for Calendar
# Using template with substitutions for Vcalendar record.


# vcf_record - string
# vcs_template - string
def process_vcf_record(vcf_record, vcs_template):
    full_date = re.match(r'.*BDAY\;.*?\:(\d{4})\-(\d{2})-(\d{2})', vcf_record, re.DOTALL)
    if full_date is not None:
        full_date_string = ""
        date_for_description = full_date.group(3) + '-' + full_date.group(2) + '-' + full_date.group(1)
        for group in full_date.groups():
            full_date_string += group
        start_date = full_date_string + "T120000"
        end_date = full_date_string + "T120500"
    else:
        return None
    full_name = re.match(r'.*N\;.*?\:(.*?)\;(.*?)\;(.*?)\;(.*?)\;', vcf_record, re.DOTALL)
    full_name_string = ""
    for group in full_name.groups():
        full_name_string += group + ' '

    # set subject name
    vcs_template = re.sub(r'\$subj_name', full_name_string, vcs_template, flags=re.DOTALL)
    # set event description
    vcs_template = re.sub(r'\$description\_str',
                          full_name_string + date_for_description,
                          vcs_template,
                          flags=re.DOTALL)
    # set event start date
    vcs_template = re.sub(r'\$start\_event\_date', start_date, vcs_template, flags=re.DOTALL)
    # set event end date
    vcs_template = re.sub(r'\$end\_event\_date', end_date, vcs_template, flags=re.DOTALL)

    return vcs_template


# vcf_path - string
# vcs_template - string
def vcf_to_vcs_converter(vcf_path, vcs_template, vcs_destination):
    vcf_file = None
    vcs_file_content = None
    result_vcs_file = None
    try:
        vcf_file = open(vcf_path, 'r')
        vcs_file = open(vcs_template, 'r')
        vcs_file_content = vcs_file.read()
        # remove comments from template
        vcs_file_content = re.sub(r'\#.*\n', '\n', vcs_file_content)
        # remove empty lines
        vcs_file_content = re.sub(r'\n{2,10}', '', vcs_file_content)
        contact_buff = ""
        result_counter = 0
        for row in vcf_file:
            if re.match(r'^BEGIN', row) is not None:
                contact_buff = ""
                continue
            elif re.match(r'^END', row) is not None:
                contact_buff = re.sub(r'\r', '', contact_buff)
                fill_vcs_record = process_vcf_record(contact_buff, vcs_file_content)
                if fill_vcs_record is not None:
                    result_vcs_file = open(vcs_destination + str(result_counter) + ".vcs", 'w+')
                    result_vcs_file.write(fill_vcs_record + '\n')
                    result_vcs_file.close()
                    result_counter += 1
            contact_buff += row
    except:
        print('Unknown exception: ' + traceback.format_exc())
    finally:
        if vcf_file is not None: vcf_file.close()
        if vcs_file is not None: vcs_file.close()
        if result_vcs_file is not None: result_vcs_file.close()

# runing
vcf_path = "/Users/Vano/Dropbox/Development/vcf_to_vcs/contacts_all_refactor.vcf"
vcs_template = "/Users/Vano/Dropbox/Development/vcf_to_vcs/template.vcs"
vcs_destination = "/Users/Vano/dev/vcf_to_vcs/result" # template for file name
vcf_to_vcs_converter(vcf_path, vcs_template, vcs_destination)