import os
from dataclasses import dataclass


@dataclass
class BigqueryDataConfig:
    data_project_id: str
    dataset_id: str
    schema: str

    @classmethod
    def from_env(cls) -> "BigqueryDataConfig":
        """Create configuration from environment variables.

        Returns:
            BigqueryDataConfig: Configuration instance populated from environment variables.

        Raises:
            KeyError: If required environment variables are not set.
        """
        return cls(
            data_project_id=os.environ["BQ_DATA_PROJECT_ID"],
            dataset_id=os.environ["BQ_DATASET_ID"],
            schema="""
                table: `products`
                columns:
                - product_id (STRING): 商品ID
                - product_name (STRING): 商品名
                - price (FLOAT64): 価格
                - category (STRING): カテゴリ

                example_values:
                product_id | product_name | price | category
                ---------- | ------------ | ----- | --------
                'P001'     | 'ノートPC'    | 99800 | '電子機器'
                'P002'     | 'マウス'      | 2980  | '周辺機器'
                'P003'     | 'キーボード'  | 8900  | '周辺機器'
            """,
        )