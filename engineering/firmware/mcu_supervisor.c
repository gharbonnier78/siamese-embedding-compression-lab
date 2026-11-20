#include "mcu_supervisor.h"
#include <stddef.h>

/* Simulation-only policy logic; drivers and protective circuits must be reviewed.
   Keep NIR emitter OFF in sleep/fault, and preserve fault event in bounded queue. */
#define EDGE_QUEUE_MAX 256u
void edge_init(EdgeSupervisor *s) {
    if (!s) return;
    s->mode=EDGE_SLEEP; s->last_wake=WAKE_NONE;
    s->wake_events=0; s->fault_events=0;
    s->queue_pending=0; s->queue_overflows=0;
    s->power_good=true; s->nir_interlock_ok=false;
}
void edge_wake(EdgeSupervisor *s, WakeCause cause) {
    if (!s || s->mode==EDGE_FAULT || !s->power_good) return;
    s->mode=EDGE_AWAKE;
    s->last_wake=cause;
    s->wake_events++;
}
void edge_sleep(EdgeSupervisor *s) {
    if (!s || s->mode==EDGE_FAULT) return;
    s->mode=EDGE_SLEEP;
}
void edge_power_fault(EdgeSupervisor *s) {
    if (!s) return;
    s->power_good=false; s->mode=EDGE_FAULT;
    s->fault_events++;
    (void)edge_queue_event(s);
}
void edge_set_nir_interlock(EdgeSupervisor *s, bool safe) {
    if (s) s->nir_interlock_ok=safe;
}
bool edge_nir_allowed(const EdgeSupervisor *s) {
    return s && s->power_good && s->mode==EDGE_AWAKE && s->nir_interlock_ok;
}
bool edge_queue_event(EdgeSupervisor *s) {
    if (!s) return false;
    if (s->queue_pending>=EDGE_QUEUE_MAX) {
        s->queue_overflows++;
        return false;
    }
    s->queue_pending++;
    return true;
}
void edge_ack_event(EdgeSupervisor *s) {
    if (s && s->queue_pending) s->queue_pending--;
}
