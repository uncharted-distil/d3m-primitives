import sys
import os
import typing
import logging

import numpy as np
import pandas as pd
from d3m.primitive_interfaces.base import CallResult
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from d3m import container, utils
from d3m.metadata import hyperparams, params, base as metadata_base
from d3m.exceptions import PrimitiveNotFittedError
from tslearn.neighbors import KNeighborsTimeSeriesClassifier
from tslearn.preprocessing import TimeSeriesScalerMinMax

__author__ = "Distil"
__version__ = "1.2.1"
__contact__ = "mailto:cbethune@uncharted.software"

Inputs = container.DataFrame
Outputs = container.DataFrame

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


class Params(params.Params):
    scaler: TimeSeriesScalerMinMax
    classifier: KNeighborsTimeSeriesClassifier
    output_columns: pd.Index


class Hyperparams(hyperparams.Hyperparams):
    n_neighbors = hyperparams.UniformInt(
        lower=0,
        upper=sys.maxsize,
        default=5,
        semantic_types=[
            "https://metadata.datadrivendiscovery.org/types/TuningParameter"
        ],
        description="number of neighbors on which to make classification decision",
    )
    distance_metric = hyperparams.Enumeration(
        default="euclidean",
        semantic_types=[
            "https://metadata.datadrivendiscovery.org/types/TuningParameter"
        ],
        values=["euclidean", "dtw"],
        description="whether to use euclidean or dynamic time warping distance metric in KNN computation",
    )
    sample_weighting = hyperparams.Enumeration(
        default="uniform",
        semantic_types=[
            "https://metadata.datadrivendiscovery.org/types/TuningParameter"
        ],
        values=["uniform", "inverse_distance"],
        description="whether to weight points uniformly or by the inverse of their distance",
    )


class KaninePrimitive(
    SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]
):
    """
    Primitive that applies the k nearest neighbor classification algorithm to time series data.
    The tslearn KNeighborsTimeSeriesClassifier implementation is wrapped.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            "id": "2d6d3223-1b3c-49cc-9ddd-50f571818268",
            "version": __version__,
            "name": "kanine",
            "keywords": [
                "time series",
                "knn",
                "k nearest neighbor",
                "time series classification",
            ],
            "source": {
                "name": __author__,
                "contact": __contact__,
                "uris": [
                    "https://github.com/uncharted-distil/d3m-primitives",
                ],
            },
            "installation": [
                {"type": "PIP", "package": "cython", "version": "0.29.24"},
                {
                    "type": metadata_base.PrimitiveInstallationType.PIP,
                    "package_uri": "git+https://github.com/uncharted-distil/d3m-primitives.git@{git_commit}#egg=kf-d3m-primitives".format(
                        git_commit=utils.current_git_commit(os.path.dirname(__file__)),
                    ),
                },
            ],
            "python_path": "d3m.primitives.time_series_classification.k_neighbors.Kanine",
            "algorithm_types": [
                metadata_base.PrimitiveAlgorithmType.K_NEAREST_NEIGHBORS,
            ],
            "primitive_family": metadata_base.PrimitiveFamily.TIME_SERIES_CLASSIFICATION,
        }
    )

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0) -> None:

        super().__init__(hyperparams=hyperparams, random_seed=random_seed)

        self._knn = KNeighborsTimeSeriesClassifier(
            n_neighbors=self.hyperparams["n_neighbors"],
            metric=self.hyperparams["distance_metric"],
            weights=self.hyperparams["sample_weighting"],
        )
        self._scaler = TimeSeriesScalerMinMax()
        self._is_fit = False

    def get_params(self) -> Params:
        if not self._is_fit:
            return Params(scaler=None, classifier=None, output_columns=None)

        return Params(
            scaler=self._scaler,
            classifier=self._knn,
            output_columns=self._output_columns,
        )

    def set_params(self, *, params: Params) -> None:
        self._scaler = params["scaler"]
        self._knn = params["classifier"]
        self._output_columns = params["output_columns"]
        self._is_fit = all(param is not None for param in params.values())

    def _get_cols(self, input_metadata):
        """private util function that finds grouping column from input metadata

        Arguments:
            input_metadata {D3M Metadata object} -- D3M Metadata object for input frame

        Returns:
            list[int] -- list of column indices annotated with GroupingKey metadata
        """

        # find column with ts value through metadata
        grouping_column = input_metadata.list_columns_with_semantic_types(
            ("https://metadata.datadrivendiscovery.org/types/GroupingKey",)
        )
        return grouping_column

    def _get_value_col(self, input_metadata):
        """
        private util function that finds the value column from input metadata

        Arguments:
        input_metadata {D3M Metadata object} -- D3M Metadata object for input frame

        Returns:
        int -- index of column that contains time series value after Time Series Formatter primitive
        """

        # find attribute column but not file column
        attributes = input_metadata.list_columns_with_semantic_types(
            ("https://metadata.datadrivendiscovery.org/types/Attribute",)
        )
        # this is assuming alot, but timeseries formaters typicaly place value column at the end
        attribute_col = attributes[-1]
        return attribute_col

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        """Sets primitive's training data

        Arguments:
            inputs {Inputs} -- D3M dataframe containing attributes
            outputs {Outputs} -- D3M dataframe containing targets
        """

        # load and reshape training data
        self._output_columns = outputs.columns
        outputs = np.array(outputs)
        n_ts = outputs.shape[0]
        ts_sz = inputs.shape[0] // n_ts

        attribute_col = self._get_value_col(inputs.metadata)
        self._X_train = inputs.iloc[:, attribute_col].values.reshape(n_ts, ts_sz)
        self._y_train = np.array(outputs).reshape(
            -1,
        )

    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        """Fits KNN model using training data from set_training_data and hyperparameters

        Keyword Arguments:
            timeout {float} -- timeout, not considered (default: {None})
            iterations {int} -- iterations, not considered (default: {None})

        Returns:
            CallResult[None]
        """

        scaled = self._scaler.fit_transform(self._X_train)
        self._knn.fit(scaled, self._y_train)
        self._is_fit = True
        return CallResult(None, has_finished=self._is_fit)

    def produce(
        self, *, inputs: Inputs, timeout: float = None, iterations: int = None
    ) -> CallResult[Outputs]:
        """Produce primitive's classifications for new time series data

        Arguments:
            inputs {Inputs} -- full D3M dataframe, containing attributes, key, and target

        Keyword Arguments:
            timeout {float} -- timeout, not considered (default: {None})
            iterations {int} -- iterations, not considered (default: {None})

        Raises:
            PrimitiveNotFittedError: if primitive not fit

        Returns:
            CallResult[Outputs] -- dataframe with a column containing a predicted class
                for each input time series
        """

        if not self._is_fit:
            raise PrimitiveNotFittedError("Primitive not fitted.")

        # find column with ts value through metadata
        grouping_column = self._get_cols(inputs.metadata)

        n_ts = inputs.iloc[:, grouping_column[0]].nunique()
        ts_sz = inputs.shape[0] // n_ts
        attribute_col = self._get_value_col(inputs.metadata)
        x_vals = inputs.iloc[:, attribute_col].values.reshape(n_ts, ts_sz)

        # make predictions
        scaled = self._scaler.transform(x_vals)
        preds = self._knn.predict(scaled)

        # create output frame
        result_df = container.DataFrame(
            {self._output_columns[0]: preds}, generate_metadata=True
        )
        result_df.metadata = result_df.metadata.add_semantic_type(
            (metadata_base.ALL_ELEMENTS, 0),
            ("https://metadata.datadrivendiscovery.org/types/PredictedTarget"),
        )

        return CallResult(result_df, has_finished=True)
