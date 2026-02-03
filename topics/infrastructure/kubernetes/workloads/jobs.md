# Jobs

A Job is a controller for tasks that run to completion rather than continuously.
It creates Pods and ensures a specified number successfully terminate (exit
code 0). Once finished, the Job is considered complete.

## Use Cases

Jobs handle one-off tasks:

- **Database migrations:** Schema updates before a new deployment
- **Batch processing:** Processing image queues, generating reports, running
  calculations
- **Backups:** Creating disk snapshots or database dumps
- **Cleanup:** Removing old files from storage

## Retry Behavior

The Job controller is persistent. If a Pod fails (process crash or node death),
the Job starts a new Pod until reaching `backoffLimit` (default: 6 retries).

## Configuration Options

| Field                   | Description                                       | Default |
|-------------------------|---------------------------------------------------|---------|
| `completions`           | Pods that must succeed for Job completion         | 1       |
| `parallelism`           | Maximum concurrent Pods                           | 1       |
| `backoffLimit`          | Retry attempts before marking Job as failed       | 6       |
| `activeDeadlineSeconds` | Timeout; terminates all Pods and fails if reached | None    |

With 10 completions and parallelism of 2, Kubernetes runs 2 Pods at a time until
10 have succeeded.

## Example Manifest

A Job that calculates Pi to 2000 places:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-calculator
spec:
  template:
    spec:
      containers:
        - name: pi
          image: perl:5.34
          command: [ "perl", "-Mbignum=bpi", "-wle", "print bpi(2000)" ]
      restartPolicy: Never
  backoffLimit: 4
```

**Restart policy constraint:** Jobs require `restartPolicy: OnFailure` or
`Never`. Using `Always` would conflict with the Job's goal of completing and
stopping.

## Job vs Deployment

| Feature        | Deployment           | Job                             |
|----------------|----------------------|---------------------------------|
| Goal           | Keep Pods running    | Complete task and exit          |
| Exit behavior  | Restarts Pod on exit | Success if exit code is 0       |
| Use case       | Web server, API      | Migration, batch script, backup |
| Restart policy | Always               | OnFailure or Never              |

## Cleanup

Completed Jobs and their Pods are not deleted automatically—they remain in
`Completed` state for log inspection. Clean up by:

- Deleting the Job manually (also deletes its Pods)
- Setting `ttlSecondsAfterFinished` to auto-delete after a duration

## Related

- [Deployments](deployments.md) - For continuously running applications
