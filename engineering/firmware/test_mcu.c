#include <assert.h>
#include <stdbool.h>
#include "mcu_supervisor.h"
int main(void) {
    EdgeSupervisor s;
    edge_init(&s);
    assert(s.mode==EDGE_SLEEP && !edge_nir_allowed(&s));
    edge_set_nir_interlock(&s,true);
    assert(!edge_nir_allowed(&s));
    edge_wake(&s,WAKE_PRESENCE);
    assert(s.mode==EDGE_AWAKE && s.last_wake==WAKE_PRESENCE);
    assert(edge_nir_allowed(&s));
    edge_sleep(&s);
    assert(!edge_nir_allowed(&s));
    assert(edge_queue_event(&s));
    edge_ack_event(&s);
    assert(s.queue_pending==0);
    edge_wake(&s,WAKE_TAMPER);
    edge_power_fault(&s);
    assert(s.mode==EDGE_FAULT && !edge_nir_allowed(&s));
    assert(s.queue_pending==1 && s.fault_events==1);
    edge_wake(&s,WAKE_PRESENCE);
    assert(s.mode==EDGE_FAULT);
    return 0;
}
