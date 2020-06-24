from setuptools import setup, find_packages

setup(
    name="kf-d3m-primitives",
    version="0.4.0",
    description="All Kung Fu D3M primitives as a single library",
    packages=find_packages(),
    setkeywords=['d3m_primitive'],
    install_requires=[
        "d3m",
        "tslearn",
        "statsmodels",
        "pmdarima>=1.6.1",
        "hdbscan",
        "requests",
        "shap>=0.35.0",
        "torchvision==0.5.0",
        "gluonts", 
        "albumentations",
        "tifffile",
        "scikit-image==0.16.1",
        "tensorflow-gpu==2.2.0",
        "punk @ git+https://github.com/uncharted-distil/punk@8b101eca26b5f9a3df2a65aab2733bd404965578#egg=punk",
        "object_detection_retinanet @ git+https://github.com/uncharted-distil/object-detection-retinanet@f02652a00b3cd81a5c37f5c34da0daaa541dffb1#egg=object_detection_retinanet",
        "Simon @ git+https://github.com/uncharted-distil/simon@00422bbdc9caa09b867f8b5f583487b59b605de0#egg=Simon-1.2.5",
        "nk_sent2vec @ git+https://github.com/uncharted-distil/nk-sent2vec@08a74ce1aff98e81eda2f3211ad7f7015bfa8124#egg=nk_sent2vec",
        "duke @ git+https://github.com/uncharted-distil/duke@c56416e959b52ff5077c5a54c329e2f6e83bbd97#egg=duke",
        "rsp @ git+https://github.com/cfld/rs_pretrained@92d832efe1961d6a06011f689dad7ef2481a64b1#egg=rsp"
    ],
    entry_points={
        "d3m.primitives": [
            "data_cleaning.column_type_profiler.Simon = primitives.data_preprocessing.data_typing.simon:SimonPrimitive",
            "data_cleaning.geocoding.Goat_forward = primitives.data_preprocessing.geocoding_forward.goat_forward:GoatForwardPrimitive",
            "data_cleaning.geocoding.Goat_reverse = primitives.data_preprocessing.geocoding_reverse.goat_reverse:GoatReversePrimitive",
            "feature_extraction.nk_sent2vec.Sent2Vec = primitives.natural_language_processing.sent2vec.sent2vec:Sent2VecPrimitive",
            "clustering.k_means.Sloth = primitives.clustering.k_means.Storc:StorcPrimitive",
            "clustering.hdbscan.Hdbscan = primitives.clustering.hdbscan.Hdbscan:HdbscanPrimitive",
            "clustering.spectral_graph.SpectralClustering = primitives.clustering.spectral_clustering.spectral_clustering:SpectralClusteringPrimitive",
            "dimensionality_reduction.t_distributed_stochastic_neighbor_embedding.Tsne = primitives.dimensionality_reduction.tsne.Tsne:TsnePrimitive",
            "time_series_classification.k_neighbors.Kanine = primitives.ts_classification.knn.kanine:KaninePrimitive",
            "time_series_forecasting.vector_autoregression.VAR = primitives.ts_forecasting.vector_autoregression.var:VarPrimitive",
            "time_series_classification.convolutional_neural_net.LSTM_FCN = primitives.ts_classification.lstm_fcn.lstm_fcn:LstmFcnPrimitive",
            "time_series_forecasting.lstm.DeepAR = primitives.ts_forecasting.deep_ar.deepar:DeepArPrimitive",
            "object_detection.retina_net.ObjectDetectionRN = primitives.object_detection.retinanet.object_detection_retinanet:ObjectDetectionRNPrimitive",
            "data_cleaning.data_cleaning.Datacleaning = primitives.data_preprocessing.data_cleaning.data_cleaning:DataCleaningPrimitive",
            "data_cleaning.text_summarization.Duke = primitives.data_preprocessing.text_summarization.duke:DukePrimitive",
            "feature_selection.pca_features.Pcafeatures = primitives.feature_selection.pca_features.pca_features:PcaFeaturesPrimitive",
            "feature_selection.rffeatures.Rffeatures = primitives.feature_selection.rf_features.rf_features:RfFeaturesPrimitive",
            "classification.inceptionV3_image_feature.Gator = primitives.image_classification.imagenet_transfer_learning.gator:GatorPrimitive",
            "remote_sensing.remote_sensing_pretrained.RemoteSensingPretrained = primitives.remote_sensing.featurizer.remote_sensing_pretrained:RemoteSensingPretrainedPrimitive",
        ],
    },
)
