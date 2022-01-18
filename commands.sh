rm -rf runs/default_offline && CUDA_VISIBLE_DEVICES=0 python train.py \
                               --train-config experiment_params/train_config_default.yaml \
                               --dataset-config experiment_params/dataset_offline_default.yaml

rm -rf runs/default_EGNN && CUDA_VISIBLE_DEVICES=1 python train.py \
                            --train-config experiment_params/train_config_EGNN.yaml \
                            --dataset-config experiment_params/dataset_offline_default.yaml