<?php 
    function convert_charset($item) 
        { 
		        if ($unserialize = unserialize($item)) 
				        { 
						            foreach ($unserialize as $key => $value) 
								                { 
											                $unserialize[$key] = @iconv('windows-1256', 'UTF-8', $value); 
													            } 
							                $serialize = serialize($unserialize); 
							                return $serialize; 
									        } 
			        else 
					        { 
							            return @iconv('windows-1256', 'UTF-8', $item); 
								            } 
			    } 
?>
