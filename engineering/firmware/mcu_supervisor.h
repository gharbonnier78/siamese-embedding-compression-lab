#ifndef SIAMESE_MCU_SUPERVISOR_H
#define SIAMESE_MCU_SUPERVISOR_H
#include <stdbool.h>
#include <stdint.h>

/* No hardware registers or battery-control GPIO are connected in this demo. */
typedef enum { EDGE_SLEEP=0, EDGE_AWAKE=1, EDGE_FAULT=2 } EdgeMode;
typedef enum { WAKE_NONE=0, WAKE_PRESENCE=1, WAKE_TAMPER=2, WAKE_POWER=3 } WakeCause;
typedef struct {
    EdgeMode mode;
    WakeCause last_wake;
    uint32_t wake_events;
    uint32_t fault_events;
    uint32_t queue_pending;
    uint32_t queue_overflows;
    bool power_good;
    bool nir_interlock_ok;
} EdgeSupervisor;

void edge_init(EdgeSupervisor *s);
void edge_wake(EdgeSupervisor *s, WakeCause cause);
void edge_sleep(EdgeSupervisor *s);
void edge_power_fault(EdgeSupervisor *s);
void edge_set_nir_interlock(EdgeSupervisor *s, bool safe);
bool edge_nir_allowed(const EdgeSupervisor *s);
bool edge_queue_event(EdgeSupervisor *s);
void edge_ack_event(EdgeSupervisor *s);
#endif
