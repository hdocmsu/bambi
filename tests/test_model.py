import pytest
from bambi.models import Term, Model
from os.path import dirname, join
import pandas as pd


@pytest.fixture(scope="module")
def diabetes_data():
    from os.path import dirname, join
    data_dir = join(dirname(__file__), 'data')
    data = pd.read_csv(join(data_dir, 'diabetes.txt'), sep='\t')
    data['age_grp'] = 0
    data['age_grp'][data['AGE'] > 40] = 1
    data['age_grp'][data['AGE'] > 60] = 2
    return data


@pytest.fixture(scope="module")
def base_model(diabetes_data):
    return Model(diabetes_data)


def test_term_init(diabetes_data):
    model = Model(diabetes_data)
    term = Term(model, 'BMI', diabetes_data['BMI'])
    # Test that all defaults are properly initialized
    assert term.name == 'BMI'
    assert term.categorical == False
    assert term.type_ == 'fixed'
    assert term.levels is not None
    assert term.data.shape == (442, 1)


def test_term_split(diabetes_data):
    # Split a continuous fixed variable
    model = Model(diabetes_data)
    model.add_term('BMI', split_by='age_grp')
    assert model.terms['BMI'].data.shape == (442, 3)
    # Split a categorical fixed variable
    model.reset()
    model.add_term('BMI', split_by='age_grp', categorical=True)
    assert model.terms['BMI'].data.shape == (442, 489)
    # Split a continuous random variable
    model.reset()
    model.add_term('BMI', split_by='age_grp', categorical=False, random=True)
    assert model.terms['BMI'].data.shape == (442, 3)
    # Split a categorical random variable
    model.reset()
    model.add_term('BMI', split_by='age_grp', categorical=True, random=True)
    t = model.terms['BMI'].data
    assert isinstance(t, dict)
    assert t['age_grp[0]'].shape == (442, 83)


def test_model_init(diabetes_data):

    model = Model(diabetes_data)
    assert hasattr(model, 'data')
    # assert model.intercept
    # assert len(model.terms) == 1
    # assert 'Intercept' in model.terms
    assert model.y is None
    assert hasattr(model, 'backend')

    model = Model(diabetes_data, intercept=False)
    assert not model.terms


def test_add_term_to_model(diabetes_data):

    model = Model(diabetes_data)
    model.add_term('BMI')
    assert isinstance(model.terms['BMI'], Term)
    model.add_term('age_grp', random=False, categorical=True)
    # Test that arguments are passed appropriately onto Term initializer
    model.add_term('BP', random=True, split_by='age_grp', categorical=True)
    assert isinstance(model.terms['BP'], Term)
    # assert list(model.terms['BP'].data.values())[0].shape == (442, 99, 2)

