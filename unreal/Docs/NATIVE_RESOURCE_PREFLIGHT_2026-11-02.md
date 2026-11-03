# Optional resource gate for the Windows native review

Run from an isolated, clean checkout before any new Unreal Engine 5.8.4 native verification:

```powershell
pwsh -NoProfile -File unreal/Tools/Test-NativeResourceHeadroom.ps1 -Checkout .
pwsh -NoProfile -File unreal/Tools/Test-NativeResourceHeadroom.ps1 -SelfTest
```

The gate is **read-only** and intentionally separate from `Verify-Unreal.ps1`.
It conservatively requires 25 GiB available on the checkout's volume and
6 GiB currently free physical RAM. These are operational safety thresholds
for this review workstation, **not** Unreal's official hardware minimums.
An insufficient machine returns exit code 2, without launching a build,
writing a SaveGame, modifying configuration, or creating evidence. An error
also does not grant permission to run a build.

Passing the resource probe **does not** establish clean source custody,
Editor build success, 25 successful native automations, P01–P13 PIE,
approved art, Starbourne authorization, or release eligibility. Before any
native run, explicitly pin the exact head, preserve hashes of tracked INI
files, isolate the run from existing user data, and keep prior receipts.
