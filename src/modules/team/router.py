from fastapi import APIRouter, Depends, HTTPException
from .dto import TeamDto, TeamMemberDto
from .models import Team, TeamMember
from src.common.permissions import get_current_user
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("")
async def create_team(body: TeamDto, user=Depends(get_current_user)):
    organization_id = user.attributes.get("organization_id")

    if not organization_id:
        raise HTTPException(403, "Not authorization")

    record = await Team.find_one(
        where={"name": {"mode": "insensitive", "value": body.name}}
    )

    if record:
        raise HTTPException(400, "Duplicate record")

    return await Team.create(
        name=body.name, description=body.description, organization_id=organization_id
    )


@router.get("")
async def get_teams(user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    if not organizationId:
        raise HTTPException(403, "Not authorized")

    return await Team.filter(where={"organization_id": organizationId})


@router.put("/{team_id}")
async def update_data(team_id: int, body: TeamDto, user=Depends(get_current_user)):
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

    return await Team.update(
        team_id,
        name=body.name,
        description=body.description,
        organization_id=organizationId,
    )


@router.delete("/{team_id}")
async def delete_team(team_id: int, user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    if not organizationId:
        raise HTTPException(403, "Not authorized")
    return await Team.delete(team_id)


@router.put("/{team_id}/assign-member")
async def assign_team_member(
    team_id: int, body: TeamMemberDto, user=Depends(get_current_user)
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
        if member:
            member.delete()

    return {"message": "Team members updated successfully"}


@router.get("/{team_id}/team-members")
async def get_team_members(team_id: int):

    members = await TeamMember.filter(
        where={"team_id": team_id}, options=[selectinload(TeamMember.user)]
    )

    return [
        {**member.dict(), "user": member.user.dict() if member.user else None}
        for member in members
    ]
