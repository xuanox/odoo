��    M      �  g   �      �  	   �  �  �  �  �  #   A
  $   e
     �
     �
     �
     �
     �
     �
     �
     �
     �
     �
     �
  
   	  
             3     I     V     d     q     v  	   }     �     �     �     �     �     �     �     �      �          <     ?     P     `     p     w     �  *   �     �     �     �     �  	   �  #   �     
     "     ?     E     L     T     c     r          �  
   �     �     �     �     �     �     �     �               -     :     I     N     [     h  C  k  
   �  �  �  �  �  #   W  %   {  !   �     �     �  
   �     �     �     �     �     �            
   *  	   5  $   ?  $   d     �     �     �     �     �     �  	   �  
   �  	                  %     .     A  	   H     R     X     [     t     �     �  
   �     �  )   �  	   �                      %   !     G  &   e     �     �  	   �     �     �     �     �     �     �     �          #     (     8     M     g     �     �     �     �     �     �     �     �           
                                )           6   7           =   E   .              &      	   "       8   I         @   ;   0   +                 C   5           H   (      B   :   2       /      !   ?          %      F      #         A       >   4   $       L      9   '   G       *   M      D           -   1       K           <         ,            3             J       # Reports <?xml version="1.0"?>
<div>
    Dear ${object.sudo().partner_id.name or 'Madam/Sir'},<br/><br/>
    Your request
    % if object.access_token:
    <a href="/helpdesk/ticket/${object.id}/${object.access_token}">${object.name}</a>
    % endif
    has been received and is Customer Pending.
    The reference of your ticket is ${object.id}.<br/><br/>
    To add additional comments, reply to this email.<br/>
    Thanks you,<br/><br/>
    ${object.team_id.name or 'Helpdesk'} Team.
</div>
         <?xml version="1.0"?>
<div>
    Dear ${object.sudo().team_id.name or 'Madam/Sir'},<br/><br/>
    Your request
    % if object.access_token:
    <a href="/helpdesk/ticket/${object.id}/${object.access_token}">${object.name}</a>
    % endif
    has been received and is pending to assign a responsible.
    The reference of ticket is ${object.id}.<br/><br/>
    Thanks you,<br/><br/>
    ${object.company_id.name or 'Helpdesk'} Team.
</div>
         <i class="fa fa-comment"/> Feedback <i class="fa fa-download"/> Download <i class="fa fa-print"/> Print Active Assign Ticket Assigned to Brand Cancel Cause Cause Ticket Client Cliente Config Settings Created by Created on Dealer Warranty End Dealer Warranty Start Detail Causa Detail Reason Display Name Done Emails Equipment Equipment Modality Equipment Number Equipment Relation Equipment State Equipo Helpdesk Helpdesk Team Helpdesk Ticket Helpdesk Ticket - Pending Reason Helpdesk Ticket - cause Reason ID Last Modified on Last Updated by Last Updated on Leader Location Mail Reception Mail where the new ticket will be received Modality Modality Team Model Name New Order New Ticket - ${object.display_name} New Ticket Notification New Ticket Notification Mail Order Orders Pending Pending Reason Pending Ticket Planned Date Remote Attention Reports Serial no. Settings Setup your domain alias Team Team Leader Team Responsible Technical Support Order Technical Support Orders Ticket Ticket and TSO Warranty End Warranty Start Zone cause Reason cause Ticket or Project-Id-Version: Odoo Server 12.0+e
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2019-06-11 18:11+0000
PO-Revision-Date: 2019-06-11 16:16-0500
Last-Translator: <>
Language-Team: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
Language: es
X-Generator: Poedit 2.2.3
 # Reportes <?xml version="1.0"?>
<div>
    Estimado ${object.sudo().partner_id.name or 'Madam/Sir'},<br/><br/>
    Su Solicitud
    % if object.access_token:
    <a href="/helpdesk/ticket/${object.id}/${object.access_token}">${object.name}</a>
    % endif
    recibida esta pendiente la programación.
    La referencia del Ticket es ${object.id}.<br/><br/>
    Otra consulta adicional nos escribe a este email.<br/>
    Gracias,<br/><br/>
    ${object.team_id.name or 'Helpdesk'}.
</div>
         <?xml version="1.0"?>
<div>
    Estimado ${object.sudo().team_id.name or 'Madam/Sir'},<br/><br/>
    La Solicitud
    % if object.access_token:
    <a href="/helpdesk/ticket/${object.id}/${object.access_token}">${object.name}</a>
    % endif
    recibida esta pendiente por asignar un responsable.
    La referencia del Ticket es ${object.id}.<br/><br/>
    Gracias,<br/><br/>
    ${object.company_id.name or 'Helpdesk'}.
</div>
         <i class="fa fa-comment"/> Opinión <i class="fa fa-download"/> Descargar <i class="fa fa-print"/> Imprimir Activo Asignar Ticket Asignada a Marca Cancelar Causa Causa Cliente Cliente Opciones de Configuración Creado por Creado el Fin de la Garantía del distribuidor Inicio de Garantía del distribuidor Detalle de la Causa Detalle de la Razón Nombre mostrado Cerrar Ticket Correos electrónicos Equipo Modalidad N° Equipo Relación Estado del Equipo Equipo Helpdesk Equipo de Helpdesk Ticket Pendiente Causa ID Última modificación en Última actualización por Última actualización el Lider Ubicación Email de Recepción Correo donde se recibirá el nuevo ticket Modalidad Team Modelo Nombre Nueva Orden Nuevo Ticket - ${object.display_name} Notificación de Nuevo Ticket Email de Notificación de Nuevo Ticket Orden Pedidos Pendiente Razón - Pendiente Ticket Pendiente Fecha Planeada Atención Remota Reportes N° Serial. Ajustes Configure su alias de dominio Team Líder del Team Responsable del Team Orden de Soporte Técnico Ordenes de Soporte Técnico Ticket Ticket y TSO Fin de la Garantía Inicio de la Garantía Zona causa - Detalle causa o 