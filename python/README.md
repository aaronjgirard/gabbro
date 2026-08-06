# gabbro

**Open source seismic processing you can read, fork, and cite.**

> ⚠️ **Pre-alpha (0.0.1).** This is a placeholder release that reserves the
> name on PyPI and validates the release pipeline. There is no usable API yet.
> Follow progress at [gabbro.ca](https://gabbro.ca).

```bash
pip install gabbro
```

## What gabbro will do

- **I/O** — read and write SEG-Y, SU, and SEG-D without a C toolchain.
- **Processing** — script-first flows: deconvolution, NMO, stacking, migration.
- **Provenance** — every flow is a script, so a stack is reproducible from raw
  field data.

## Planned usage

```python
import gabbro as gb

shot = gb.read_segy("line-42.sgy")
gathers = shot.sort("cdp").nmo(velocity=gb.velocity.from_picks("picks.csv"))
stack = gathers.stack()
stack.plot()
```

## License

Apache-2.0. Developed in the open at
[github.com/aaronjgirard/gabbro](https://github.com/aaronjgirard/gabbro).
