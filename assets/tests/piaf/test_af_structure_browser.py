from utils.piaf.af_structure_browser import AfStructureBrowser

TEST_STRUCTURE = [
    {
        "name": "NuGreen",
        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
        "attributes": [
            {
                "name": "test"
            }
        ],
        "assets": [
            {
                "name": "Little Rock",
                "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
                "attributes": [
                    {
                        "name": "test"
                    }
                ],
                "assets": [
                    {
                        "name": "Extruding Process",
                        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
                        "description": "Current percent savings in energy use.",
                        "assets": [],
                        "attributes": [
                            {
                                "name": "test"
                            }
                        ],
                    }
                ]
            },
            {
                "name": "Second Extruding Process",
                "description": "Description 2",
                "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
                "template": "Boiler",
                "attributes": [
                    {
                        "name": "test"
                    }
                ],
            }
        ]
    }
]


def test_search_assets_by_name():
    #given
    browser = AfStructureBrowser(
        assets_query="Extruding Process"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "description": "Current percent savings in energy use.",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }
    assert expected == actual


def test_search_assets_by_name_wildcards():
    #given
    browser = AfStructureBrowser(
        assets_query="Extruding.*"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "description": "Current percent savings in energy use.",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }
    assert expected == actual


def test_search_assets_by_path():
    #given
    browser = AfStructureBrowser(
        assets_query=".*Little Rock\\Extruding Process.*",
        assets_field="path"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "description": "Current percent savings in energy use.",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }
    assert expected == actual


def test_search_assets_by_name_multiple():
    #given
    browser = AfStructureBrowser(
        assets_query=".*Extruding Process"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "description": "Current percent savings in energy use.",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process": {
            "name": "Second Extruding Process",
            "description": "Description 2",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
            "template": "Boiler",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }

    assert expected == actual


def test_search_assets_by_description():
    #given
    browser = AfStructureBrowser(
        assets_query="Current.*",
        assets_field="description"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "description": "Current percent savings in energy use.",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }

    assert expected == actual

def test_search_assets_by_template():
    #given
    browser = AfStructureBrowser(
        assets_query="Boiler",
        assets_field="template"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process": {
            "name": "Second Extruding Process",
            "description": "Description 2",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
            "template": "Boiler",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }

    assert expected == actual

def test_search_assets_by_name_all():
    #given
    browser = AfStructureBrowser(
        assets_query=".*"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen": {
            "name": "NuGreen",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock": {
            "name": "Little Rock",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "description": "Current percent savings in energy use.",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process": {
            "name": "Second Extruding Process",
            "description": "Description 2",
            "template": "Boiler",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }
    assert expected == actual


def test_search_assets_by_description_all():
    #given
    browser = AfStructureBrowser(
        assets_query=".*",
        assets_field="description"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen": {
            "name": "NuGreen",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock": {
            "name": "Little Rock",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "description": "Current percent savings in energy use.",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process": {
            "name": "Second Extruding Process",
            "description": "Description 2",
            "template": "Boiler",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
            "attributes": [
                {
                    "name": "test"
                }
            ]
        }
    }

    assert expected == actual

TEST_STRUCTURE_WITH_ATTRIBUTES = [
    {
        "name": "NuGreen",
        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
        "attributes": [
            {
                "name": "Fuel",
                "description": "Fuel description"
            },
            {
                "name": "Fuel2",
                "description": "Fuel description 2"
            }
        ],
        "assets": [
            {
                "name": "Little Rock",
                "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
                "description": "Current ...",
                "attributes": [
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
                "assets": [
                    {
                        "name": "Extruding Process",
                        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
                        "description": "Current percent savings in energy use.",
                        "attributes": [
                            {
                                "name": "test savings test",
                                "categories": [
                                    {
                                        "name": "test category"
                                    }
                                ]
                            }
                        ],
                    }
                ]
            },
            {
                "name": "Second Extruding Process",
                "description": "Description 2",
                "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
                "attributes": [
                    {
                        "name": "Fuel",
                        "description": "Fuel description second 2"
                    }
                ]
            }
        ]
    }
]

def test_select_attributes_by_name():
    # given
    browser = AfStructureBrowser(
        assets_query="NuGreen",
        assets_field="name",
        attributes_query="Fuel"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen": {
            "name": "NuGreen",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
            "attributes": [
                {
                    "name": "Fuel",
                    "description": "Fuel description"
                }
            ]
        }
    }
    assert expected == actual


def test_select_attributes_by_name_wildcard():
    # given
    browser = AfStructureBrowser(
        assets_query="Current.*",
        assets_field="description",
        attributes_query=".*avings.*"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock": {
            "name": "Little Rock",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
            "description": "Current ...",
            "attributes": [
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
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process": {
            "name": "Extruding Process",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock\\Extruding Process",
            "description": "Current percent savings in energy use.",
            "attributes": [
                {
                    "name": "test savings test",
                    "categories": [
                        {
                            "name": "test category"
                        }
                    ]
                }
            ]
        }
    }

    assert expected == actual


def test_select_attributes_by_description():
    # given
    browser = AfStructureBrowser(
        assets_query="NuGreen|Second Extruding Process",
        assets_field="name",
        attributes_query=".*2.*",
        attributes_field="description"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen": {
            "name": "NuGreen",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
            "attributes": [
                {
                    "name": "Fuel2",
                    "description": "Fuel description 2"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process": {
            "name": "Second Extruding Process",
            "description": "Description 2",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
            "attributes": [
                {
                    "name": "Fuel",
                    "description": "Fuel description second 2"
                }
            ]
        }
    }
    assert expected == actual


def test_select_attributes_by_category():
    # given
    browser = AfStructureBrowser(
        assets_query="Little Rock|NuGreen",
        assets_field="name",
        attributes_query="Energy Savings KPI",
        attributes_field="categories"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock": {
            "name": "Little Rock",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
            "description": "Current ...",
            "attributes": [
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
            ]
        }
    }
    assert expected == actual


def test_select_no_attributes():
    # given
    browser = AfStructureBrowser(
        assets_query=".*",
        assets_field="name",
        attributes_query="no attributes with this name",
        attributes_field="name"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    assert actual is not None
    expected = {}
    assert expected == actual


def test_select_attributes_from_all_assets():
    # given
    browser = AfStructureBrowser(
        assets_query=".*",
        assets_field="name",
        attributes_query="Fuel",
        attributes_field="name"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    assert actual is not None
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen": {
            "name": "NuGreen",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen",
            "attributes": [
                {
                    "name": "Fuel",
                    "description": "Fuel description"
                }
            ]
        },
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process": {
            "name": "Second Extruding Process",
            "description": "Description 2",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Second Extruding Process",
            "attributes": [
                {
                    "name": "Fuel",
                    "description": "Fuel description second 2"
                }
            ]
        }
    }
    assert expected == actual


def test_select_attributes_by_pi_point_name():
    # given
    browser = AfStructureBrowser(
        assets_query=".*",
        assets_field="name",
        attributes_query="SINUSOIDU_1",
        attributes_field="point"
    )

    # when
    actual = browser.search_assets(TEST_STRUCTURE_WITH_ATTRIBUTES)

    # then
    expected = {
        "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock": {
            "name": "Little Rock",
            "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\NuGreen\\Little Rock",
            "description": "Current ...",
            "attributes": [
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
            ]
        }
    }

    assert actual is not None
    assert expected == actual