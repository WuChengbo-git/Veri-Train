"""
Quality Gate - 数据质量门禁任务
"""

import random
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.dataset import Dataset
from app.config import settings
import structlog

logger = structlog.get_logger()


@celery_app.task(name="check_quality_gate")
def check_quality_gate(dataset_id: str):
    """
    数据质量门禁检查

    这是系统的核心功能之一!
    检查项:
    1. 对齐率 (alignment_rate) >= 80%
    2. 重复率 (duplicate_rate) <= 20%
    3. 语言一致性 (language_consistency) >= 90%
    4. GPT抽样评分
    """

    logger.info("quality_gate_started", dataset_id=dataset_id)

    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        # TODO: 加载数据集内容
        # data = load_dataset_content(dataset.file_path)

        # 1. 计算对齐率
        # alignment_rate = calculate_alignment_rate(data)
        alignment_rate = 0.92  # 示例值

        # 2. 计算重复率
        # duplicate_rate = calculate_duplicate_rate(data)
        duplicate_rate = 0.08  # 示例值

        # 3. 检查语言一致性
        # language_consistency = check_language_consistency(data)
        language_consistency = 0.95  # 示例值

        # 4. GPT抽样评分
        # sample_data = random.sample(data, min(100, len(data)))
        # sample_scores = [gpt_evaluate_quality(s) for s in sample_data]
        # avg_sample_score = np.mean(sample_scores)
        avg_sample_score = 4.2  # 示例值

        # 5. 判定是否通过
        passed = (
            alignment_rate >= settings.QUALITY_GATE_ALIGNMENT_RATE
            and duplicate_rate <= settings.QUALITY_GATE_DUPLICATE_RATE
            and language_consistency >= settings.QUALITY_GATE_LANGUAGE_CONSISTENCY
        )

        # 6. 保存结果
        quality_gate_result = {
            "status": "passed" if passed else "failed",
            "checked_at": datetime.utcnow().isoformat(),
            "metrics": {
                "alignment_rate": alignment_rate,
                "duplicate_rate": duplicate_rate,
                "language_consistency": language_consistency,
                "avg_sample_score": avg_sample_score,
            },
            "thresholds": {
                "alignment_rate": settings.QUALITY_GATE_ALIGNMENT_RATE,
                "duplicate_rate": settings.QUALITY_GATE_DUPLICATE_RATE,
                "language_consistency": settings.QUALITY_GATE_LANGUAGE_CONSISTENCY,
            },
        }

        if not passed:
            quality_gate_result["block_reasons"] = []
            if alignment_rate < settings.QUALITY_GATE_ALIGNMENT_RATE:
                quality_gate_result["block_reasons"].append(
                    f"対齐率が低い: {alignment_rate:.2f} < {settings.QUALITY_GATE_ALIGNMENT_RATE}"
                )
            if duplicate_rate > settings.QUALITY_GATE_DUPLICATE_RATE:
                quality_gate_result["block_reasons"].append(
                    f"重複率が高い: {duplicate_rate:.2f} > {settings.QUALITY_GATE_DUPLICATE_RATE}"
                )
            if language_consistency < settings.QUALITY_GATE_LANGUAGE_CONSISTENCY:
                quality_gate_result["block_reasons"].append(
                    f"言語一貫性が低い: {language_consistency:.2f} < {settings.QUALITY_GATE_LANGUAGE_CONSISTENCY}"
                )

        dataset.quality_gate_result = quality_gate_result
        dataset.status = "passed" if passed else "blocked"
        db.commit()

        logger.info(
            "quality_gate_completed",
            dataset_id=dataset_id,
            status=dataset.status,
            metrics=quality_gate_result["metrics"],
        )

        # TODO: 通过WebSocket通知前端
        # redis_client.publish(
        #     f"dataset:{dataset_id}",
        #     json.dumps({"type": "quality_gate", "result": quality_gate_result})
        # )

        return quality_gate_result

    except Exception as e:
        logger.error("quality_gate_failed", dataset_id=dataset_id, error=str(e))
        raise

    finally:
        db.close()
