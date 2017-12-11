import json
import os
from utils.piaf.PI_AF_structure_converter import PIAFStructureConverter
from osisoft_pi2aws_root import PROJECT_DIR


def test_convert_large_flat_input_to_tree():
    with open(os.path.join(PROJECT_DIR, 'tests/piaf/json/nugreen-pretty.json')) as json_data:
        input = json.load(json_data)
    with open(os.path.join(PROJECT_DIR, 'tests/piaf/json/nugreen-tree.json')) as json_data:
        expected = json.load(json_data)

    converter = PIAFStructureConverter(input)
    actual = converter.convert_flat_to_tree()

    assert expected == actual


def test_convert_small_flat_input_to_tree():
    converter = PIAFStructureConverter(json.loads(input))
    actual = converter.convert_flat_to_tree()

    expected = json.loads(output)
    assert expected == actual


input = r"""
{
  "elements": [
    {
      "name": "B-045",
      "attributes": [
        {
          "name": "Fuel",
          "categories": [
            {
              "name": "Real-Time Data",
              "description": ""
            }
          ],
          "description": "Relative Fuel Gas Use per ton of Feed",
          "value": {
            "value": "SINUSOID",
            "timestamp": "1/1/1970 12:00:00 AM"
          },
          "type": "System.Double",
          "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process\\Equipment\\B-045|Fuel"
        },
        {
          "name": "Water Savings",
          "categories": [
            {
              "name": "Energy Savings KPI",
              "description": "Relative energy use per ton of process feed."
            }
          ],
          "description": "Current percent savings in energy use.",
          "value": "",
          "type": "System.Double",
          "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process\\Equipment\\B-045|Water Savings",
          "point": {
            "name": "SINUSOIDU_1",
            "id": "10837",
            "path": "\\\\EC2AMAZ-0EE3VGR\\SINUSOIDU_1"
          }
        }
      ],
      "description": "Boiler B-045",
      "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process\\Equipment\\B-045"
    },
    {
      "name": "B-209",
      "attributes": [
        {
          "name": "Fuel",
          "categories": [
            {
              "name": "Real-Time Data",
              "description": ""
            }
          ],
          "description": "Relative Fuel Gas Use per ton of Feed",
          "value": "",
          "type": "System.Double",
          "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston\\Milling Process\\Equipment\\B-209|Fuel"
        }
      ],
      "description": "Boiler B-209",
      "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston\\Milling Process\\Equipment\\B-209"
    },
    {
      "name": "Houston",
      "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston",
      "description": "Houston Plant",
      "attributes": [
        {
          "name": "PlantCity",
          "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston|PlantCity",
          "description": "",
          "value": {
            "value": "Houston",
            "timestamp": "1/1/1970 12:00:00 AM"
          },
          "type": "System.String",
          "categories": [],
          "point": null
        }
      ]
    }
  ]
}
"""

output = r"""
[
  {
    "name": "NuGreen",
    "assets": [
      {
        "name": "Little Rock",
        "assets": [
          {
            "name": "Extruding Process",
            "assets": [
              {
                "name": "Equipment",
                "assets": [
                  {
                    "name": "B-045",
                    "attributes": [
                      {
                        "name": "Fuel",
                        "categories": [
                          {
                            "name": "Real-Time Data",
                            "description": ""
                          }
                        ],
                        "description": "Relative Fuel Gas Use per ton of Feed",
                        "value": {
                          "value": "SINUSOID",
                          "timestamp": "1/1/1970 12:00:00 AM"
                        },
                        "type": "System.Double",
                        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process\\Equipment\\B-045|Fuel"
                      },
                      {
                        "name": "Water Savings",
                        "categories": [
                          {
                            "name": "Energy Savings KPI",
                            "description": "Relative energy use per ton of process feed."
                          }
                        ],
                        "description": "Current percent savings in energy use.",
                        "value": "",
                        "type": "System.Double",
                        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process\\Equipment\\B-045|Water Savings",
                        "point": {
                          "name": "SINUSOIDU_1",
                          "id": "10837",
                          "path": "\\\\EC2AMAZ-0EE3VGR\\SINUSOIDU_1"
                        }
                      }
                    ],
                    "description": "Boiler B-045",
                    "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process\\Equipment\\B-045"
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "name": "Houston",
        "assets": [
          {
            "name": "Milling Process",
            "assets": [
              {
                "name": "Equipment",
                "assets": [
                  {
                    "name": "B-209",
                    "attributes": [
                    {
                      "name": "Fuel",
                      "categories": [
                        {
                          "name": "Real-Time Data",
                          "description": ""
                        }
                      ],
                      "description": "Relative Fuel Gas Use per ton of Feed",
                      "value": "",
                      "type": "System.Double",
                      "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston\\Milling Process\\Equipment\\B-209|Fuel"
                    }
                  ],
                  "description": "Boiler B-209",
                  "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston\\Milling Process\\Equipment\\B-209"
                  }
                ]
              }
            ]
          }
        ],
        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston",
        "description": "Houston Plant",
        "attributes": [
          {
            "name": "PlantCity",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Houston|PlantCity",
            "description": "",
            "value": {
              "value": "Houston",
              "timestamp": "1/1/1970 12:00:00 AM"
            },
            "type": "System.String",
            "categories": [],
            "point": null
          }
        ]      
      }
    ]
  }
]
"""