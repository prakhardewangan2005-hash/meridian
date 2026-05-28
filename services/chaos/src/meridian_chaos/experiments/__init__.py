"""Registry of available experiment types."""
from meridian_chaos.experiments.base import Experiment, ExperimentSpec
from meridian_chaos.experiments.cpu_pressure import CPUPressureExperiment
from meridian_chaos.experiments.disk_fill import DiskFillExperiment
from meridian_chaos.experiments.memory_pressure import MemoryPressureExperiment
from meridian_chaos.experiments.network_latency import NetworkLatencyExperiment
from meridian_chaos.experiments.network_loss import NetworkLossExperiment
from meridian_chaos.experiments.network_partition import NetworkPartitionExperiment

REGISTRY: dict[str, type[Experiment]] = {
    cls.kind: cls
    for cls in (
        CPUPressureExperiment,
        DiskFillExperiment,
        MemoryPressureExperiment,
        NetworkLatencyExperiment,
        NetworkLossExperiment,
        NetworkPartitionExperiment,
    )
}

__all__ = ["Experiment", "ExperimentSpec", "REGISTRY"]
