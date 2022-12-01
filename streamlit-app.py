# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 02:56:08 2022

@author: monar
"""

import streamlit as st
import cirpy
from cirpy import Molecule
import base64
import molecules_icon_generator as mig
import warnings

warnings.filterwarnings("ignore")  # brute force approach to avoid decompression bomb warning by pdf2image and PIL


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img width="300px" height="300px" src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


if __name__ == "__main__":
    if 'color_dict' not in st.session_state:
        st.session_state['color_dict'] = mig.color_map.copy()
    if 'resize_dict' not in st.session_state:
        st.session_state['resize_dict'] = mig.atom_resize.copy()
    if 'reset_color' not in st.session_state:
        st.session_state['reset_color'] = False
    if 'reset_size' not in st.session_state:
        st.session_state['reset_size'] = False

    new_color = st.session_state['color_dict']
    resize = st.session_state['resize_dict']

    if 'atom_color_select' in st.session_state and 'color_picker' in st.session_state and st.session_state['reset_color']:
        st.session_state.color_picker = new_color[st.session_state.atom_color_select]
        st.session_state['reset_color'] = False
    if 'atom_size_select' in st.session_state and 'sizes_slider' in st.session_state and st.session_state['reset_size']:
        st.session_state['reset_size'] = False

    st.set_page_config(page_title="Molecule icons")
    st.header('''
    Molecular Icons Generator!
    ''')

    st.text('''
    Generate icons of molecules from SMILES, Name, Cas-number, Inchi or InChIKey.
    ''')
    st.markdown(
        "For more options and information, check out the [GitHub repository](https://github.com/lmonari5/molecule-icon-generator.git)")

    input_type = st.selectbox("Create your icon by",
                              ['name', 'smiles', 'cas_number', 'stdinchi', 'stdinchikey'],
                              help='Choose the input info of your molecule')
    def_dict = {'name': 'paracetamol',
                'smiles': "CC(=O)Nc1ccc(cc1)O",
                'cas_number': '103-90-2',
                'stdinchi': 'InChI=1S/C8H9NO2/c1-6(10)9-7-2-4-8(11)5-3-7/h2-5,11H,1H3,(H,9,10)',
                'stdinchikey': 'RZVAJINKPMORJF-UHFFFAOYSA-N'}

    input_string = st.text_input(input_type + ' :', def_dict[input_type])

    col1, col2, col3 = st.columns(3, gap='medium')
    with col1:
        single_bonds = st.checkbox('Single bonds')
        remove_H = st.checkbox('Remove Hydrogen')
    with col2:
        h_shadow = st.checkbox('Hide shadows')
        black = st.checkbox('Black Icon')
    with col3:
        rdkit_draw = st.checkbox('Show RDKIT')
        bw = st.checkbox('Black and white')

    forms = [False, False, False, False]
    img_format = st.selectbox(
        'Download file format:',
        ('svg', 'png', 'jpeg', 'pdf'))

    for ind, img_form in enumerate(('svg', 'png', 'jpeg', 'pdf')):
        if img_form == img_format:
            forms[ind] = True

    # change the color
    col1, col2, col3 = st.columns(3, gap='medium')
    with col1:
        atom_color = st.selectbox(
            'Change the color:',
            sorted(list(mig.color_map.keys())), key='atom_color_select')
    with col2:
        new_color[atom_color] = st.color_picker(f' Pick {atom_color} color', new_color[atom_color],
                                                key="color_picker")
    with col3:
        st.write('\n')
        if st.button('Reset colours', help='Reset colours as default CPK', key='reset_color_but'):
            st.session_state['color_dict'] = mig.color_map.copy()
            new_color = st.session_state['color_dict']
            st.session_state['reset_color'] = True

    # change the size
    col1, col2, col3 = st.columns(3, gap='medium')
    with col1:
        atom_size = st.selectbox(
            'Change the size:',
            ['All atoms']+sorted(list(mig.atom_resize.keys())), key='atom_size_select')
    with col2:
        resize[atom_size] = st.slider(f'Multiply the size of {atom_size}', 0.0, 3.0, resize[atom_size], key='sizes_slider',
                                      help='''Increase or decrease the size of one specific atom''')
    with col3:
        st.write('\n')
        if st.button('Reset atoms size', help='Reset size to 1 for all atoms', key='reset_size_but'):
            st.session_state['resize_dict'] = mig.atom_resize.copy()
            resize = st.session_state['resize_dict']
            st.session_state['reset_size'] = True
    icon_size = resize['All atoms'] * 100

    # catch error when using the cirpy library
    try:
        if input_type == 'name':
            input_string = cirpy.resolve(input_string, 'smiles')
        mol = Molecule(input_string)
        iupac = mol.iupac_name
        if not iupac:
            iupac = 'not found'
        smiles = mol.smiles
    except Exception as e:
        st.write(f'''
        The cirpy python library is not able to resolve your input {input_type}.
        You can use SMILES to skip the cirpy library.
        ''')
        if input_type != 'smiles':
            st.stop()

    if input_type == 'smiles':  # if the input is a smile, use it directly ignoring the cirpy smiles
        smiles = input_string

    try:
        col1, col2, col3 = st.columns(3)
        with col1:
            pos_multi = st.slider('Image size multiplier', 0, 900, 300,
                                  help='''Multiply the position of the atoms with respect to the 2D structure.
                                  A higher multiplier leads to higher resolution.''')
        with col2:
            thickness = st.slider('Thickness', 0.0, 0.6, 0.2,
                                  help='''Bond and stroke thicknesses over the atom radius.''')
        with col3:
            shadow_light = st.slider('Shadow/outline light', 0.0, 1.0, 1 / 3,
                                     help='''Regulate the brightness of the shadow''')

        conf = not st.checkbox('Switch conformation', value=False)
        if conf:
            img_multi = pos_multi
        else:
            img_multi = pos_multi * 2 / 3
        mig.icon_print(smiles, name='molecular-icon', rdkit_svg=rdkit_draw,
                       single_bonds=single_bonds, remove_H=remove_H,
                       position_multiplier=img_multi, atom_radius=icon_size, bw=bw, radius_multi=resize,
                       atom_color=new_color, shadow=not h_shadow, black=black,
                       save_svg=forms[0], save_png=forms[1], save_jpeg=forms[2], save_pdf=forms[3],
                       thickness=thickness, shadow_light=shadow_light, nice_conformation=conf)
    except Exception as e:
            st.error(f'''
            Rdkit failed in building the structure of the molecule or the Image is too big. Full error:
            {e}''')
            if img_format != 'svg':
                st.write(f'Try to use the svg format')
            if input_type != 'smiles':
                st.write(f'Try to use the SMILES instead of {input_type} as input')
            st.stop()

    filename = 'molecular-icon.' + img_format
    with open(filename, "rb") as file:
        btn = st.download_button(label="Download icon",
                                 data=file,
                                 file_name=filename,
                                 mime=f"image/{img_format}")

    st.write('''
    Thanks for using the Molecules icons generators!
    ''')
    st.write('''
    Image SVG preview:
    ''')

    f = open("molecular-icon.svg", "r")
    svg_text = f.read()
    render_svg(svg_text)

    if rdkit_draw:
        f = open("molecular-icon_rdkit.svg", "r")
        svg_text = f.read()
        render_svg(svg_text)
        with open("molecular-icon_rdkit.svg", "rb") as file:
            btn = st.download_button(label="Download icon",
                                     data=file,
                                     file_name=filename,
                                     mime=f"image/{img_format}")
