#!/usr/bin/env python3
"""
SDF File Parser for DrugBank Structures
Extracts chemical structures and metadata from SDF files
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Atom:
    """Represents an atom in a molecular structure"""
    x: float
    y: float
    z: float
    element: str
    charge: int = 0
    stereo: int = 0

@dataclass
class Bond:
    """Represents a bond between atoms"""
    atom1: int
    atom2: int
    bond_type: int
    stereo: int = 0

@dataclass
class MolecularStructure:
    """Represents a complete molecular structure"""
    drugbank_id: str
    common_name: str
    cas_number: str
    unii: str
    synonyms: List[str]
    atoms: List[Atom]
    bonds: List[Bond]
    atom_count: int
    bond_count: int

class SDFParser:
    """Parser for SDF (Structure Data Format) files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.structures = []
    
    def parse_file(self) -> List[MolecularStructure]:
        """Parse the entire SDF file and return list of structures"""
        print(f"Parsing SDF file: {self.file_path}")
        
        with open(self.file_path, 'r') as f:
            content = f.read()
        
        # Split by structure separators ($$$$)
        structure_blocks = content.split('$$$$')
        
        # Remove empty blocks
        structure_blocks = [block.strip() for block in structure_blocks if block.strip()]
        
        print(f"Found {len(structure_blocks)} structure blocks")
        
        for i, block in enumerate(structure_blocks):
            if i % 100 == 0:
                print(f"Processing structure {i+1}/{len(structure_blocks)}")
            
            try:
                structure = self._parse_structure_block(block, i)
                if structure:
                    self.structures.append(structure)
            except Exception as e:
                print(f"Error parsing structure {i+1}: {e}")
                continue
        
        print(f"Successfully parsed {len(self.structures)} structures")
        return self.structures
    
    def _parse_structure_block(self, block: str, index: int) -> Optional[MolecularStructure]:
        """Parse a single structure block"""
        lines = block.strip().split('\n')
        
        if len(lines) < 3:
            return None
        
        # Parse header (first 3 lines)
        title = lines[0].strip()
        comment = lines[1].strip()
        
        # Parse counts line (line 3)
        counts_line = lines[2].strip()
        counts_parts = counts_line.split()
        
        if len(counts_parts) < 2:
            return None
        
        try:
            atom_count = int(counts_parts[0])
            bond_count = int(counts_parts[1])
        except ValueError:
            return None
        
        # Parse atoms (next atom_count lines)
        atoms = []
        atom_start = 3
        
        for i in range(atom_count):
            if atom_start + i >= len(lines):
                break
            
            atom_line = lines[atom_start + i]
            atom = self._parse_atom_line(atom_line)
            if atom:
                atoms.append(atom)
        
        # Parse bonds (next bond_count lines)
        bonds = []
        bond_start = atom_start + atom_count
        
        for i in range(bond_count):
            if bond_start + i >= len(lines):
                break
            
            bond_line = lines[bond_start + i]
            bond = self._parse_bond_line(bond_line)
            if bond:
                bonds.append(bond)
        
        # Parse metadata (after M END)
        metadata_start = bond_start + bond_count
        metadata = self._parse_metadata(lines[metadata_start:])
        
        return MolecularStructure(
            drugbank_id=metadata.get('drugbank_id', f'DB{index:05d}'),
            common_name=metadata.get('common_name', ''),
            cas_number=metadata.get('cas_number', ''),
            unii=metadata.get('unii', ''),
            synonyms=metadata.get('synonyms', []),
            atoms=atoms,
            bonds=bonds,
            atom_count=len(atoms),
            bond_count=len(bonds)
        )
    
    def _parse_atom_line(self, line: str) -> Optional[Atom]:
        """Parse a single atom line"""
        parts = line.split()
        if len(parts) < 4:
            return None
        
        try:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            element = parts[3]
            charge = int(parts[4]) if len(parts) > 4 else 0
            stereo = int(parts[5]) if len(parts) > 5 else 0
            
            return Atom(x, y, z, element, charge, stereo)
        except (ValueError, IndexError):
            return None
    
    def _parse_bond_line(self, line: str) -> Optional[Bond]:
        """Parse a single bond line"""
        parts = line.split()
        if len(parts) < 3:
            return None
        
        try:
            atom1 = int(parts[0]) - 1  # Convert to 0-based index
            atom2 = int(parts[1]) - 1  # Convert to 0-based index
            bond_type = int(parts[2])
            stereo = int(parts[3]) if len(parts) > 3 else 0
            
            return Bond(atom1, atom2, bond_type, stereo)
        except (ValueError, IndexError):
            return None
    
    def _parse_metadata(self, lines: List[str]) -> Dict[str, Any]:
        """Parse metadata section"""
        metadata = {}
        current_key = None
        current_value = []
        
        for line in lines:
            line = line.strip()
            
            # Check for property tags
            if line.startswith('> <'):
                # Save previous property
                if current_key and current_value:
                    metadata[current_key] = '\n'.join(current_value).strip()
                
                # Start new property
                current_key = line[3:-1].lower().replace('_', '_')
                current_value = []
            elif line and not line.startswith('>'):
                current_value.append(line)
        
        # Save last property
        if current_key and current_value:
            metadata[current_key] = '\n'.join(current_value).strip()
        
        # Parse synonyms
        if 'synonyms' in metadata:
            synonyms_text = metadata['synonyms']
            # Split by common delimiters
            synonyms = [s.strip() for s in re.split(r'[,;]', synonyms_text) if s.strip()]
            metadata['synonyms'] = synonyms
        
        return metadata
    
    def save_to_json(self, output_path: str):
        """Save parsed structures to JSON file"""
        structures_data = []
        
        for structure in self.structures:
            structure_dict = {
                'drugbank_id': structure.drugbank_id,
                'common_name': structure.common_name,
                'cas_number': structure.cas_number,
                'unii': structure.unii,
                'synonyms': structure.synonyms,
                'atom_count': structure.atom_count,
                'bond_count': structure.bond_count,
                'atoms': [
                    {
                        'x': atom.x,
                        'y': atom.y,
                        'z': atom.z,
                        'element': atom.element,
                        'charge': atom.charge,
                        'stereo': atom.stereo
                    }
                    for atom in structure.atoms
                ],
                'bonds': [
                    {
                        'atom1': bond.atom1,
                        'atom2': bond.atom2,
                        'bond_type': bond.bond_type,
                        'stereo': bond.stereo
                    }
                    for bond in structure.bonds
                ]
            }
            structures_data.append(structure_dict)
        
        output_data = {
            'version': '1.0',
            'source': 'DrugBank SDF Structures',
            'total_structures': len(structures_data),
            'structures': structures_data
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Saved {len(structures_data)} structures to {output_path}")

def main():
    """Main function to parse SDF file"""
    print("DrugBank SDF Structure Parser")
    print("=" * 40)
    
    # Parse the SDF file
    parser = SDFParser("../../datasets/raw/open structures.sdf")
    structures = parser.parse_file()
    
    if not structures:
        print("No structures found!")
        return
    
    # Save to JSON
    output_path = "../../datasets/processed/drugbank_structures.json"
    parser.save_to_json(output_path)
    
    # Show sample structures
    print(f"\nSample structures:")
    for i, structure in enumerate(structures[:5]):
        print(f"{i+1}. {structure.common_name} ({structure.drugbank_id})")
        print(f"   CAS: {structure.cas_number}")
        print(f"   UNII: {structure.unii}")
        print(f"   Atoms: {structure.atom_count}, Bonds: {structure.bond_count}")
        if structure.synonyms:
            print(f"   Synonyms: {', '.join(structure.synonyms[:3])}...")
        print()
    
    print(f"✓ Successfully parsed {len(structures)} molecular structures!")
    print(f"✓ Saved to: {output_path}")

if __name__ == "__main__":
    main()
