from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload

from src.common.context import TenantContext
from src.common.permissions import get_current_user
from src.utils.response import CustomResponse as cr

from .models import Team, TeamMember
from .schema import TeamMemberSchema, TeamSchema, TeamResponseOutSchema
from typing import List

router = APIRouter()


@router.post("")
async def create_team(body: TeamSchema, user=Depends(get_current_user)):

    if not TenantContext:
        raise HTTPException(403, "Not authorization")

    record = await Team.find_one(
        where={"name": {"mode": "insensitive", "value": body.name}}
    )

    if record:
        raise HTTPException(400, "Duplicate record")

    team = await Team.create(**body.model_dump())
    data = [team.to_json(schema=TeamResponseOutSchema)]

    return cr.success(data=data, message="Team Created Successfully")


@router.get("", response_model=List[TeamResponseOutSchema])
async def get_teams(user=Depends(get_current_user)):

    if not TenantContext:
        raise HTTPException(403, detail="Not authorized")

    teams = await Team.filter()
    data = [team.to_json(schema=TeamResponseOutSchema) for team in teams]

    return cr.success(data=data)


@router.put("/{team_id}")
async def update_data(team_id: int, body: TeamSchema, user=Depends(get_current_user)):
    # user update data
    organizationId = user.attributes.get("organization_id")

    if not organizationId:
        raise HTTPException(403, "Not authorized")

    team = await Team.get(team_id)

    if not team:
        raise HTTPException(404, "Not found")

    record = await Team.find_one(
        where={
            "name": {"mode": "insensitive", "value": body.name},
            "organization_id": organizationId,
        }
    )

    if record and record.id != team.id:
        raise HTTPException(400, "Duplicate record")

    team = await Team.update(
        team_id,
        name=body.name,
        description=body.description,
        organization_id=organizationId,
    )

    return cr.success(data=team.to_json())


@router.delete("/{team_id}")
async def delete_team(team_id: int, user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    if not organizationId:
        raise HTTPException(403, "Not authorized")
    team = await Team.soft_delete(team_id)

    return cr.success()


@router.put("/{team_id}/assign-member")
async def assign_team_member(
    team_id: int, body: TeamMemberSchema, user=Depends(get_current_user)
):
    team = await Team.get(team_id)
    if not team:
        raise HTTPException(404, "Team not found")

    # Step 1: Get current members in the team
    current_members = await TeamMember.filter(where={"team_id": team_id})
    current_user_ids = {member.user_id for member in current_members}

    # Step 2: Desired members from request
    new_user_ids = set(body.user_ids)

    # Step 3: Determine users to add and remove
    to_add = new_user_ids - current_user_ids
    to_remove = current_user_ids - new_user_ids

    # Step 4: Add new members
    for user_id in to_add:
        await TeamMember.create(team_id=team_id, user_id=user_id)

    # Step 5: Remove old members
    for user_id in to_remove:
        member = await TeamMember.find_one(
            where={"team_id": team_id, "user_id": user_id}
        )

        if not member:
            raise HTTPException(404, "Not found")
        if member:
            await TeamMember.soft_delete(member.id)

    return cr.success(data={"message": "Team members updated successfully"})


@router.get("/{team_id}/team-members")
async def get_team_members(team_id: int):

    members = await TeamMember.filter(
        where={"team_id": team_id},
        options=[selectinload(TeamMember.user)],  # type:ignore
    )

    return cr.success(data=[member.to_json() for member in members])



