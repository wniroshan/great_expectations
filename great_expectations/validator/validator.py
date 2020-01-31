"""This is currently helping bridge APIs"""
from great_expectations.dataset import PandasDataset, SqlAlchemyDataset, SparkDFDataset
from great_expectations.dataset.sqlalchemy_dataset import SqlAlchemyBatchReference
from great_expectations.util import load_class


class Validator(object):

    def __init__(self, batch, expectation_suite, expectation_engine, **kwargs):
        self.batch = batch
        self.expectation_suite = expectation_suite
        self.expectation_engine = load_class(
            class_name=expectation_engine.class_name,
            module_name=expectation_engine.module_name or "great_expectations.dataset"
        )
        self.init_kwargs = kwargs

    def get_dataset(self):
        if issubclass(self.expectation_engine, PandasDataset):
            import pandas as pd

            if not isinstance(self.batch["data"], pd.DataFrame):
                raise ValueError("PandasDataset expectation_engine requires a Pandas Dataframe for its batch")
            return self.expectation_engine(
                self.batch.data,
                expectation_suite=self.expectation_suite,
                batch_kwargs=self.batch.batch_kwargs,
                batch_parameters=self.batch.batch_parameters,
                batch_markers=self.batch.batch_markers,
                data_context=self.batch.data_context,
                **self.init_kwargs
            )

        elif issubclass(self.expectation_engine, SqlAlchemyDataset):
            if not isinstance(self.batch.data, SqlAlchemyBatchReference):
                raise ValueError("SqlAlchemyDataset expectation_engine requires a SqlAlchemyBatchReference for its batch")
            init_kwargs = self.batch.data.get_init_kwargs()
            init_kwargs.update(self.init_kwargs)
            return self.expectation_engine(
                batch_kwargs=self.batch.batch_kwargs,
                batch_parameters=self.batch.batch_parameters,
                batch_markers=self.batch.batch_markers,
                data_context=self.batch.data_context,
                expectation_suite=self.expectation_suite,
                **init_kwargs
            )

        elif issubclass(self.expectation_engine, SparkDFDataset):
            import pyspark
            caching = self.init_kwargs.pop("caching", True)

            if not isinstance(self.batch.data, pyspark.sql.DataFrame):
                raise ValueError("SparkDFDataset expectation_engine requires a spark DataFrame for its batch")
            return self.expectation_engine(
                spark_df=self.batch.data,
                expectation_suite=self.expectation_suite,
                batch_kwargs=self.batch.batch_kwargs,
                batch_parameters=self.batch.batch_parameters,
                batch_markers=self.batch.batch_markers,
                data_context=self.batch.data_context,
                caching=caching,
                **self.init_kwargs
            )